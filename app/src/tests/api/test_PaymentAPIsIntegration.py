import pytest
import json
from decimal import Decimal
from datetime import date, timedelta
from django.test import Client
from django.urls import reverse

from accounts.models import CustomUserModel
from partners.models import Partner
from products.models import StockDay
from trade.models import Order, Invoice, Payment, PaymentDetail


@pytest.mark.django_db
class TestPaymentAPIsIntegration:
    """Tests de integración para los endpoints de pagos"""

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
            total_price=Decimal('2000.00'),
            total_margin=Decimal('200.00')
        )

        # Crear múltiples facturas para probar pagos parciales
        self.invoice1 = Invoice.objects.create(
            order=self.order,
            partner=self.customer,
            num_invoice='FAC-001',
            type_document='FAC_VENTA',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_price=Decimal('1200.00'),
            total_margin=Decimal('120.00'),
            status='PENDIENTE'
        )

        self.invoice2 = Invoice.objects.create(
            order=self.order,
            partner=self.customer,
            num_invoice='FAC-002',
            type_document='FAC_VENTA',
            date=date.today(),
            due_date=date.today() + timedelta(days=30),
            total_price=Decimal('800.00'),
            total_margin=Decimal('80.00'),
            status='PENDIENTE'
        )

    def test_full_payment_lifecycle(self):
        """Test del ciclo completo: crear, obtener, actualizar y eliminar pago"""
        
        # 1. Crear un pago inicial
        create_url = reverse('payment_create_list')
        payment_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "800.00"
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "200.00"
                }
            ]
        }

        create_response = self.client.post(
            create_url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert create_response.status_code == 201
        payment_id = create_response.json()['payment_id']

        # 2. Obtener el pago creado
        get_url = reverse('payment_detail_update', args=[payment_id])
        get_response = self.client.get(get_url)

        assert get_response.status_code == 200
        payment_data_response = get_response.json()
        assert payment_data_response['amount'] == '1000.00'
        assert payment_data_response['method'] == 'EFECTIVO'
        assert len(payment_data_response['invoices']) == 2

        # 3. Actualizar el pago
        update_data = {
            "amount": "1500.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP123456",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1200.00"
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "300.00"
                }
            ]
        }

        update_response = self.client.put(
            get_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert update_response.status_code == 200

        # Verificar actualización
        get_response_after_update = self.client.get(get_url)
        updated_data = get_response_after_update.json()
        assert updated_data['amount'] == '1500.00'
        assert updated_data['method'] == 'TRANSF'
        assert updated_data['bank'] == 'BANCO PICHINCHA'

        # 4. Eliminar el pago
        delete_url = reverse('payment_delete', args=[payment_id])
        delete_response = self.client.delete(delete_url)

        assert delete_response.status_code == 200

        # 5. Verificar que el pago se eliminó (soft delete)
        payment = Payment.objects.get(id=payment_id)
        assert not payment.is_active

    def test_multiple_payments_same_invoice(self):
        """Test para aplicar múltiples pagos a la misma factura"""
        
        create_url = reverse('payment_create_list')
        
        # Primer pago parcial
        payment1_data = {
            "date": str(date.today()),
            "amount": "500.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "500.00"
                }
            ]
        }

        response1 = self.client.post(
            create_url,
            data=json.dumps(payment1_data),
            content_type='application/json'
        )
        assert response1.status_code == 201
        payment1_id = response1.json()['payment_id']

        # Segundo pago parcial para la misma factura
        payment2_data = {
            "date": str(date.today()),
            "amount": "700.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP123456",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "700.00"
                }
            ]
        }

        response2 = self.client.post(
            create_url,
            data=json.dumps(payment2_data),
            content_type='application/json'
        )
        assert response2.status_code == 201
        payment2_id = response2.json()['payment_id']

        # Verificar que ambos pagos existen y apuntan a la misma factura
        payment_details = PaymentDetail.objects.filter(
            invoice=self.invoice1
        )
        assert payment_details.count() == 2

        total_paid = sum(detail.amount for detail in payment_details)
        assert total_paid == Decimal('1200.00')  # 500 + 700

        # Eliminar ambos pagos en lote
        delete_url = reverse('payment_delete_bulk')
        delete_data = {
            "payment_ids": [payment1_id, payment2_id]
        }

        delete_response = self.client.post(
            delete_url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert delete_response.status_code == 200
        delete_result = delete_response.json()
        assert len(delete_result['deleted_payments']) == 2

    def test_payment_distributed_across_invoices(self):
        """Test para pago distribuido entre múltiples facturas"""
        
        create_url = reverse('payment_create_list')
        
        # Pago que cubre ambas facturas
        payment_data = {
            "date": str(date.today()),
            "amount": "2000.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP789012",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1200.00"  # Cubre toda la factura 1
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "800.00"   # Cubre toda la factura 2
                }
            ]
        }

        response = self.client.post(
            create_url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        payment_id = response.json()['payment_id']

        # Verificar que se crearon los detalles correctos
        payment_details = PaymentDetail.objects.filter(
            payment_id=payment_id
        )
        assert payment_details.count() == 2

        # Verificar distribución
        detail_invoice1 = payment_details.get(invoice=self.invoice1)
        detail_invoice2 = payment_details.get(invoice=self.invoice2)
        
        assert detail_invoice1.amount == Decimal('1200.00')
        assert detail_invoice2.amount == Decimal('800.00')

    def test_error_handling_sequence(self):
        """Test para secuencia de manejo de errores"""
        
        # 1. Intentar crear pago con datos inválidos
        create_url = reverse('payment_create_list')
        invalid_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            # Falta method e invoices
        }

        response = self.client.post(
            create_url,
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        assert response.status_code == 400

        # 2. Crear pago válido
        valid_data = {
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

        response = self.client.post(
            create_url,
            data=json.dumps(valid_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        payment_id = response.json()['payment_id']

        # 3. Confirmar el pago (simular cambio de estado)
        payment = Payment.objects.get(id=payment_id)
        payment.status = 'CONFIRMADO'
        payment.save()

        # 4. Intentar actualizar pago confirmado
        update_url = reverse('payment_detail_update', args=[payment_id])
        update_data = {"amount": "1500.00"}

        response = self.client.put(
            update_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert response.status_code == 400

        # 5. Intentar eliminar pago confirmado
        delete_url = reverse('payment_delete', args=[payment_id])
        response = self.client.delete(delete_url)
        assert response.status_code == 400

        # 6. Verificar que el pago sigue activo
        payment.refresh_from_db()
        assert payment.is_active
        assert payment.status == 'CONFIRMADO'

    def test_pagination_and_listing(self):
        """Test para paginación y listado de pagos"""
        
        # Crear múltiples pagos
        create_url = reverse('payment_create_list')
        payment_ids = []

        for i in range(25):  # Crear 25 pagos
            payment_data = {
                "date": str(date.today()),
                "amount": f"{100 + i * 10}.00",
                "method": "EFECTIVO",
                "invoices": [
                    {
                        "invoice_id": self.invoice1.id,
                        "amount": f"{100 + i * 10}.00"
                    }
                ]
            }

            response = self.client.post(
                create_url,
                data=json.dumps(payment_data),
                content_type='application/json'
            )
            assert response.status_code == 201
            payment_ids.append(response.json()['payment_id'])

        # Probar paginación
        list_url = reverse('payment_create_list')
        
        # Primera página
        response = self.client.get(list_url + '?page=1&page_size=10')
        assert response.status_code == 200
        data = response.json()
        assert len(data['payments']) == 10
        assert data['page'] == 1

        # Segunda página
        response = self.client.get(list_url + '?page=2&page_size=10')
        assert response.status_code == 200
        data = response.json()
        assert len(data['payments']) == 10
        assert data['page'] == 2

        # Tercera página (parcial)
        response = self.client.get(list_url + '?page=3&page_size=10')
        assert response.status_code == 200
        data = response.json()
        assert len(data['payments']) >= 5  # Al menos 5 pagos restantes
        assert data['page'] == 3
