import pytest
import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import Client
from django.urls import reverse
from django.db import models

from accounts.models import CustomUserModel
from partners.models import Partner
from products.models import StockDay
from trade.models import Order, Invoice, Payment, PaymentDetail


@pytest.mark.django_db
class TestCollectionsCreateUpdateAPI:

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

    def test_create_collection_success(self):
        """Test para crear un cobro exitosamente"""
        url = reverse('collection_create_list')
        
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

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'collection' in data
        assert data['collection']['amount'] == "1500.00"
        assert data['collection']['method'] == "TRANSF"

        # Verificar que se creó el cobro con type_transaction='INGRESO'
        collection = Payment.objects.get(id=data['collection']['id'])
        assert collection.type_transaction == 'INGRESO'
        assert collection.amount == Decimal('1500.00')
        assert collection.payment_number.startswith('COL-')

        # Verificar que se crearon los detalles
        details = PaymentDetail.objects.filter(payment=collection)
        assert details.count() == 2
        assert details.aggregate(total=models.Sum('amount'))['total'] == Decimal('1500.00')

    def test_create_collection_missing_required_fields(self):
        """Test para validar campos requeridos en la creación de cobro"""
        url = reverse('collection_create_list')
        
        # Datos incompletos (falta fecha)
        collection_data = {
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                }
            ]
        }

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Campo requerido: date' in data['error']

    def test_create_collection_no_invoices(self):
        """Test para validar que se requieren facturas"""
        url = reverse('collection_create_list')
        
        collection_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": []
        }

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Debe especificar al menos una factura' in data['error']

    def test_create_collection_amount_mismatch(self):
        """Test para validar que el monto total coincida con las facturas"""
        url = reverse('collection_create_list')
        
        collection_data = {
            "date": str(date.today()),
            "amount": "2000.00",  # Monto mayor que la suma de facturas
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                }
            ]
        }

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'El monto total de facturas no puede exceder el monto del cobro' in data['error']

    def test_create_collection_invalid_invoice(self):
        """Test para validar facturas inexistentes"""
        url = reverse('collection_create_list')
        
        collection_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": 99999,  # ID que no existe
                    "amount": "1000.00"
                }
            ]
        }

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Factura no encontrada' in data['error']

    def test_update_collection_success(self):
        """Test para actualizar un cobro exitosamente"""
        # Crear un cobro primero
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE'
        )

        PaymentDetail.objects.create(
            payment=collection,
            invoice=self.invoice1,
            amount=Decimal('1000.00')
        )

        url = reverse('collection_detail_update', kwargs={'collection_id': collection.id})
        
        update_data = {
            "amount": "1200.00",
            "method": "TRANSF",
            "bank": "BANCO INTERNACIONAL",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1200.00"
                }
            ]
        }

        response = self.client.put(
            url, 
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        # Verificar que se actualizó el cobro
        collection.refresh_from_db()
        assert collection.amount == Decimal('1200.00')
        assert collection.method == 'TRANSF'
        assert collection.bank == 'BANCO INTERNACIONAL'

    def test_update_collection_not_found(self):
        """Test para actualizar un cobro inexistente"""
        url = reverse('collection_detail_update', kwargs={'collection_id': 99999})
        
        update_data = {
            "amount": "1200.00",
            "method": "TRANSF"
        }

        response = self.client.put(
            url, 
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Cobro no encontrado' in data['error']

    def test_get_collection_detail(self):
        """Test para obtener detalles de un cobro específico"""
        # Crear un cobro con detalles
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1500.00'),
            method='TRANSF',
            status='PENDIENTE',
            bank='BANCO TEST',
            nro_operation='OP123456'
        )

        PaymentDetail.objects.create(
            payment=collection,
            invoice=self.invoice1,
            amount=Decimal('1000.00')
        )

        PaymentDetail.objects.create(
            payment=collection,
            invoice=self.invoice2,
            amount=Decimal('500.00')
        )

        url = reverse('collection_detail_update', kwargs={'collection_id': collection.id})
        
        response = self.client.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'collection' in data
        assert data['collection']['amount'] == "1500.00"
        assert data['collection']['method'] == "TRANSF"
        assert data['collection']['bank'] == "BANCO TEST"
        assert len(data['collection']['invoices']) == 2

    def test_get_collection_list(self):
        """Test para obtener lista de cobros con paginación"""
        # Crear varios cobros de prueba
        for i in range(15):
            Payment.objects.create(
                date=date.today(),
                type_transaction='INGRESO',
                amount=Decimal(f'{1000 + i}.00'),
                method='EFECTIVO',
                status='PENDIENTE'
            )

        url = reverse('collection_create_list')
        
        # Test paginación por defecto
        response = self.client.get(url)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'collections' in data
        assert 'pagination' in data
        assert len(data['collections']) == 10  # page_size por defecto

        # Test paginación personalizada
        response = self.client.get(url + '?page=2&page_size=5')
        assert response.status_code == 200
        data = json.loads(response.content)
        assert len(data['collections']) == 5
        assert data['pagination']['page'] == 2

    def test_create_collection_with_bank_validation(self):
        """Test para validar campos requeridos según método de pago"""
        url = reverse('collection_create_list')
        
        # Para transferencias, banco y operación son requeridos
        collection_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "TRANSF",
            # Faltan banco y nro_operation
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1000.00"
                }
            ]
        }

        response = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        # Debería crear el cobro pero con una advertencia en validación
        assert response.status_code in [200, 400]
        
        # Si se crea, verificar que se genera el número COL-
        if response.status_code == 200:
            data = json.loads(response.content)
            collection = Payment.objects.get(id=data['collection']['id'])
            assert collection.payment_number.startswith('COL-')

    def test_collection_number_generation(self):
        """Test para verificar la generación correcta de números de cobro"""
        url = reverse('collection_create_list')
        
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

        # Crear primer cobro
        response1 = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response1.status_code == 200
        data1 = json.loads(response1.content)
        assert data1['collection']['payment_number'] == 'COL-000001'

        # Crear segundo cobro
        response2 = self.client.post(
            url, 
            data=json.dumps(collection_data),
            content_type='application/json'
        )

        assert response2.status_code == 200
        data2 = json.loads(response2.content)
        assert data2['collection']['payment_number'] == 'COL-000002'

    def test_collection_filters_by_type_transaction(self):
        """Test para verificar que solo se obtienen cobros (INGRESO) y no pagos (EGRESO)"""
        # Crear un pago (EGRESO)
        Payment.objects.create(
            date=date.today(),
            type_transaction='EGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE'
        )

        # Crear un cobro (INGRESO)
        Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE'
        )

        url = reverse('collection_create_list')
        response = self.client.get(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        
        # Solo debe retornar el cobro, no el pago
        assert len(data['collections']) == 1
        
        # Verificar que es un cobro
        collection_in_response = data['collections'][0]
        collection_obj = Payment.objects.get(id=collection_in_response['id'])
        assert collection_obj.type_transaction == 'INGRESO'
