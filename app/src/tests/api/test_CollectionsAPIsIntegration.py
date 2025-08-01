import pytest
import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import Client
from django.urls import reverse
from django.db.models import Sum

from accounts.models import CustomUserModel
from partners.models import Partner
from products.models import StockDay
from trade.models import Order, Invoice, Payment, PaymentDetail


@pytest.mark.django_db
class TestCollectionsAPIsIntegration:

    def setup_method(self):
        """Configuración de datos de prueba antes de cada test"""
        self.client = Client()

        # Crear usuario de prueba
        self.user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        self.client.force_login(self.user)

        # Crear partner/cliente de prueba
        self.customer = Partner.objects.create(
            business_tax_id="TEST_CUSTOMER_001",
            name="Cliente Test S.A.",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )

        # Crear StockDay de prueba
        self.stock_day = StockDay.objects.create(
            date=date.today(),
            is_active=True
        )

        # Crear orden de prueba
        self.order = Order.objects.create(
            stock_day=self.stock_day,
            partner=self.customer,
            type_document='ORD_VENTA',
            num_order='TEST-001',
            delivery_date=date.today() + timedelta(days=7),
            status='CONFIRMADO',
            total_price=Decimal('1000.00'),
            total_margin=Decimal('100.00')
        )

        # Crear facturas de prueba
        self.invoice1 = Invoice.objects.create(
            order=self.order,
            partner=self.customer,
            num_invoice='FAC-001',
            type_document='FAC_VENTA',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_price=Decimal('1000.00'),
            total_margin=Decimal('100.00'),
            status='PENDIENTE'
        )

        self.invoice2 = Invoice.objects.create(
            order=self.order,
            partner=self.customer,
            num_invoice='FAC-002',
            type_document='FAC_VENTA',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_price=Decimal('500.00'),
            total_margin=Decimal('50.00'),
            status='PENDIENTE'
        )

    def test_complete_collection_lifecycle(self):
        """Test del ciclo completo: crear, leer, actualizar y eliminar cobro"""

        # 1. CREAR cobro
        create_url = reverse('collection_create_list')
        collection_data = {
            "date": str(date.today()),
            "amount": "1500.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP123456789",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "500.00"
                }
            ]
        }

        create_response = self.client.post(
            create_url,
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert create_response.status_code == 200
        create_data = json.loads(create_response.content)
        assert create_data['success'] is True
        collection_id = create_data['collection']['id']

        # 2. LEER cobro creado
        detail_url = reverse('collection_detail_update',
                             kwargs={'collection_id': collection_id})

        detail_response = self.client.get(detail_url)
        assert detail_response.status_code == 200
        detail_data = json.loads(detail_response.content)
        assert detail_data['success'] is True
        assert detail_data['collection']['amount'] == "1500.00"
        assert len(detail_data['collection']['invoices']) == 2

        # 3. ACTUALIZAR cobro
        update_data = {
            "amount": "1200.00",
            "method": "EFECTIVO",
            "bank": "",
            "nro_operation": "",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1200.00"
                }
            ]
        }

        update_response = self.client.put(
            detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert update_response.status_code == 200
        update_data_response = json.loads(update_response.content)
        assert update_data_response['success'] is True

        # Verificar actualización
        verify_response = self.client.get(detail_url)
        verify_data = json.loads(verify_response.content)
        assert verify_data['collection']['amount'] == "1200.00"
        assert verify_data['collection']['method'] == "EFECTIVO"
        assert len(verify_data['collection']['invoices']) == 1

        # 4. ELIMINAR cobro
        delete_url = reverse('collection_delete',
                             kwargs={'collection_id': collection_id})

        delete_response = self.client.delete(delete_url)
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.content)
        assert delete_data['success'] is True

        # Verificar que fue eliminado (soft delete)
        collection = Payment.objects.get(id=collection_id)
        assert collection.is_active is False

    def test_collection_and_payment_separation(self):
        """Test para verificar que cobros y pagos se mantienen separados"""

        # Crear un pago (EGRESO)
        payment = Payment.objects.create(
            date=date.today(),
            type_transaction='EGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='PAY-000001'
        )

        # Crear un cobro usando la API
        create_url = reverse('collection_create_list')
        collection_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                }
            ]
        }

        create_response = self.client.post(
            create_url,
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert create_response.status_code == 200

        # Obtener lista de cobros
        list_response = self.client.get(create_url)
        list_data = json.loads(list_response.content)

        # Solo debe aparecer el cobro, no el pago
        assert len(list_data['collections']) == 1
        collection_in_list = list_data['collections'][0]

        # Verificar que es un cobro (INGRESO)
        collection_obj = Payment.objects.get(id=collection_in_list['id'])
        assert collection_obj.type_transaction == 'INGRESO'
        assert collection_obj.payment_number.startswith('COL-')

        # Verificar que el pago sigue existiendo pero separado
        payment.refresh_from_db()
        assert payment.type_transaction == 'EGRESO'
        assert payment.payment_number.startswith('PAY-')

    def test_sequential_collection_numbers(self):
        """Test para verificar numeración secuencial de cobros"""
        create_url = reverse('collection_create_list')

        # Crear múltiples cobros
        for i in range(3):
            collection_data = {
                "date": str(date.today()),
                "amount": f"{1000 + i * 100}.00",
                "method": "EFECTIVO",
                "invoices": [
                    {
                        "invoice_id": self.invoice1.id,
                        "amount": f"{1000 + i * 100}.00"
                    }
                ]
            }

            response = self.client.post(
                create_url,
                data=json.dumps(collection_data),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.content)
            expected_number = f"COL-{i + 1:06d}"
            assert data['collection']['payment_number'] == expected_number

    def test_bulk_delete_collections(self):
        """Test para eliminación masiva de cobros"""
        create_url = reverse('collection_create_list')
        collection_ids = []

        # Crear múltiples cobros
        for i in range(5):
            collection_data = {
                "date": str(date.today()),
                "amount": f"{1000 + i * 100}.00",
                "method": "EFECTIVO",
                "status": "PENDIENTE" if i < 3 else "CONFIRMADO",
                "invoices": [
                    {
                        "invoice_id": self.invoice1.id,
                        "amount": f"{1000 + i * 100}.00"
                    }
                ]
            }

            response = self.client.post(
                create_url,
                data=json.dumps(collection_data),
                content_type='application/json'
            )

            assert response.status_code == 200
            data = json.loads(response.content)
            collection_ids.append(data['collection']['id'])

        # Intentar eliminar todos (algunos deberían fallar por estar confirmados)
        delete_url = reverse('collection_delete_bulk')
        delete_data = {
            "collection_ids": collection_ids
        }

        delete_response = self.client.post(
            delete_url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert delete_response.status_code == 200
        delete_result = json.loads(delete_response.content)
        assert delete_result['success'] is True

        # Verificar que se eliminaron solo los pendientes
        assert delete_result['summary']['successfully_deleted'] == 3
        assert delete_result['summary']['errors_count'] == 2

        # Verificar estado de cada cobro
        for i, collection_id in enumerate(collection_ids):
            collection = Payment.objects.get(id=collection_id)
            if i < 3:  # PENDIENTES - deberían estar eliminados
                assert collection.is_active is False
            else:  # CONFIRMADOS - deberían seguir activos
                assert collection.is_active is True

    def test_pagination_with_collections(self):
        """Test para verificar paginación en lista de cobros"""
        create_url = reverse('collection_create_list')

        # Crear múltiples cobros
        for i in range(25):
            collection_data = {
                "date": str(date.today()),
                "amount": f"{1000 + i}.00",
                "method": "EFECTIVO",
                "invoices": [
                    {
                        "invoice_id": self.invoice1.id,
                        "amount": f"{1000 + i}.00"
                    }
                ]
            }

            response = self.client.post(
                create_url,
                data=json.dumps(collection_data),
                content_type='application/json'
            )
            assert response.status_code == 200

        # Test página 1 (por defecto)
        list_response = self.client.get(create_url)
        list_data = json.loads(list_response.content)
        assert len(list_data['collections']) == 10  # page_size por defecto
        assert list_data['pagination']['page'] == 1
        assert list_data['pagination']['total_count'] == 25
        assert list_data['pagination']['total_pages'] == 3

        # Test página 2 con tamaño personalizado
        list_response = self.client.get(create_url + '?page=2&page_size=8')
        list_data = json.loads(list_response.content)
        assert len(list_data['collections']) == 8
        assert list_data['pagination']['page'] == 2

    def test_collection_detail_with_multiple_invoices(self):
        """Test para verificar detalles de cobro con múltiples facturas"""
        create_url = reverse('collection_create_list')

        collection_data = {
            "date": str(date.today()),
            "amount": "1500.00",
            "method": "TRANSF",
            "bank": "BANCO TEST",
            "nro_operation": "OP123456",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "500.00"
                }
            ]
        }

        create_response = self.client.post(
            create_url,
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        collection_id = json.loads(create_response.content)['collection']['id']

        # Obtener detalles
        detail_url = reverse('collection_detail_update',
                             kwargs={'collection_id': collection_id})
        detail_response = self.client.get(detail_url)
        detail_data = json.loads(detail_response.content)

        # Verificar estructura de respuesta
        collection = detail_data['collection']
        assert collection['amount'] == "1500.00"
        assert collection['method'] == "TRANSF"
        assert collection['bank'] == "BANCO TEST"
        assert collection['nro_operation'] == "OP123456"

        # Verificar facturas asociadas
        invoices = collection['invoices']
        assert len(invoices) == 2

        amounts = [float(inv['amount']) for inv in invoices]
        assert 1000.00 in amounts
        assert 500.00 in amounts

        invoice_numbers = [inv['invoice_number'] for inv in invoices]
        assert 'FAC-001' in invoice_numbers
        assert 'FAC-002' in invoice_numbers

    def test_error_handling_across_apis(self):
        """Test para verificar manejo de errores consistente"""

        # Test crear cobro con datos inválidos
        create_url = reverse('collection_create_list')
        invalid_data = {
            "date": "invalid-date",
            "amount": "not-a-number",
            "method": "INVALID_METHOD",
            "invoices": []
        }

        response = self.client.post(
            create_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'error' in data

        # Test obtener cobro inexistente
        detail_url = reverse('collection_detail_update',
                             kwargs={'collection_id': 99999})
        response = self.client.get(detail_url)

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Cobro no encontrado' in data['error']

        # Test eliminar cobro inexistente
        delete_url = reverse('collection_delete',
                             kwargs={'collection_id': 99999})
        response = self.client.delete(delete_url)

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Cobro no encontrado' in data['error']
