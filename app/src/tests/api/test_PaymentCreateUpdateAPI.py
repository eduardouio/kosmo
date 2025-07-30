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
class TestPaymentCreateUpdateAPI:

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

    def test_create_payment_success(self):
        """Test para crear un pago exitosamente"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "date": str(date.today()),
            "amount": "1500.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP123456789",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1100.00"
                },
                {
                    "invoice_id": self.invoice2.id,
                    "amount": "400.00"
                }
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        data = response.json()
        assert 'payment_id' in data
        assert 'payment_number' in data
        assert data['message'] == 'Payment created successfully'

        # Verificar que el pago se creó en la base de datos
        payment = Payment.objects.get(id=data['payment_id'])
        assert payment.amount == Decimal('1500.00')
        assert payment.method == 'TRANSF'
        assert payment.bank == 'BANCO PICHINCHA'
        assert payment.payment_number is not None

        # Verificar que se crearon los detalles de pago
        payment_details = PaymentDetail.objects.filter(payment=payment)
        assert payment_details.count() == 2

    def test_create_payment_missing_required_fields(self):
        """Test para crear pago sin campos requeridos"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "amount": "1500.00",
            # Falta date, method, invoices
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'Missing required field' in data['error']

    def test_create_payment_no_invoices(self):
        """Test para crear pago sin facturas"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "date": str(date.today()),
            "amount": "1500.00",
            "method": "EFECTIVO",
            "invoices": []
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'At least one invoice is required'

    def test_create_payment_amount_mismatch(self):
        """Test para crear pago donde el monto no coincide con la suma de facturas"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "date": str(date.today()),
            "amount": "2000.00",  # No coincide con la suma de invoices
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1100.00"
                }
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'does not match sum of invoice amounts' in data['error']

    def test_create_payment_invalid_invoice(self):
        """Test para crear pago con factura que no existe"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "date": str(date.today()),
            "amount": "1000.00",
            "method": "EFECTIVO",
            "invoices": [
                {
                    "invoice_id": 99999,  # No existe
                    "amount": "1000.00"
                }
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'does not exist' in data['error']

    def test_create_payment_method_requires_bank(self):
        """Test para método de pago que requiere banco"""
        url = reverse('payment_create_list')
        
        payment_data = {
            "date": str(date.today()),
            "amount": "1100.00",
            "method": "TRANSF",
            # Falta bank y nro_operation
            "invoices": [
                {
                    "invoice_id": self.invoice1.id,
                    "amount": "1100.00"
                }
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(payment_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'banco es requerido' in data['error'] or 'número de operación es requerido' in data['error']

    def test_update_payment_success(self):
        """Test para actualizar un pago exitosamente"""
        # Crear pago inicial
        payment = Payment.objects.create(
            date=date.today(),
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE'
        )
        payment.payment_number = Payment.get_next_payment_number()
        payment.save()

        # Crear detalle inicial
        PaymentDetail.objects.create(
            payment=payment,
            invoice=self.invoice1,
            amount=Decimal('1000.00')
        )

        url = reverse('payment_detail_update', args=[payment.id])
        
        update_data = {
            "amount": "1500.00",
            "method": "TRANSF",
            "bank": "BANCO PICHINCHA",
            "nro_operation": "OP987654321",
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

        response = self.client.put(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Payment updated successfully'

        # Verificar cambios en la base de datos
        payment.refresh_from_db()
        assert payment.amount == Decimal('1500.00')
        assert payment.method == 'TRANSF'
        assert payment.bank == 'BANCO PICHINCHA'

        # Verificar que se actualizaron los detalles
        payment_details = PaymentDetail.objects.filter(payment=payment)
        assert payment_details.count() == 2

    def test_update_payment_not_found(self):
        """Test para actualizar pago que no existe"""
        url = reverse('payment_detail_update', args=[99999])
        
        update_data = {
            "amount": "1500.00",
            "method": "EFECTIVO"
        }

        response = self.client.put(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        data = response.json()
        assert data['error'] == 'Payment not found'

    def test_update_confirmed_payment(self):
        """Test para actualizar pago confirmado (no debe permitirse)"""
        payment = Payment.objects.create(
            date=date.today(),
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='CONFIRMADO'  # Ya confirmado
        )

        url = reverse('payment_detail_update', args=[payment.id])
        
        update_data = {
            "amount": "1500.00"
        }

        response = self.client.put(
            url,
            data=json.dumps(update_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert 'Cannot update a confirmed or rejected payment' in data['error']

    def test_get_payment_detail(self):
        """Test para obtener detalles de un pago"""
        payment = Payment.objects.create(
            date=date.today(),
            amount=Decimal('1500.00'),
            method='TRANSF',
            bank='BANCO PICHINCHA',
            nro_operation='OP123456',
            status='PENDIENTE'
        )
        payment.payment_number = Payment.get_next_payment_number()
        payment.save()

        # Crear detalles
        PaymentDetail.objects.create(
            payment=payment,
            invoice=self.invoice1,
            amount=Decimal('1000.00')
        )
        PaymentDetail.objects.create(
            payment=payment,
            invoice=self.invoice2,
            amount=Decimal('500.00')
        )

        url = reverse('payment_detail_update', args=[payment.id])
        response = self.client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data['id'] == payment.id
        assert data['amount'] == '1500.00'
        assert data['method'] == 'TRANSF'
        assert data['bank'] == 'BANCO PICHINCHA'
        assert len(data['invoices']) == 2

    def test_get_payment_not_found(self):
        """Test para obtener pago que no existe"""
        url = reverse('payment_detail_update', args=[99999])
        response = self.client.get(url)

        assert response.status_code == 404
        data = response.json()
        assert data['error'] == 'Payment not found'

    def test_list_payments(self):
        """Test para listar pagos con paginación"""
        # Crear algunos pagos
        for i in range(5):
            payment = Payment.objects.create(
                date=date.today(),
                amount=Decimal(f'{1000 + i * 100}.00'),
                method='EFECTIVO',
                status='PENDIENTE'
            )
            payment.payment_number = Payment.get_next_payment_number()
            payment.save()

        url = reverse('payment_create_list')
        response = self.client.get(url + '?page=1&page_size=3')

        assert response.status_code == 200
        data = response.json()
        assert 'payments' in data
        assert 'page' in data
        assert 'page_size' in data
        assert data['page'] == 1
        assert data['page_size'] == 3
        assert len(data['payments']) <= 3

    def test_create_payment_invalid_json(self):
        """Test para crear pago con JSON inválido"""
        url = reverse('payment_create_list')
        
        response = self.client.post(
            url,
            data="invalid json",
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'Invalid JSON'

    def test_create_payment_empty_body(self):
        """Test para crear pago con body vacío"""
        url = reverse('payment_create_list')
        
        response = self.client.post(
            url,
            data="",
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'No data provided'
