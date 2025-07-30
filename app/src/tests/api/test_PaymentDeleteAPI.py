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
class TestPaymentDeleteAPI:

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

        # Crear factura de prueba
        self.invoice = Invoice.objects.create(
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

        # Crear pagos de prueba
        self.payment1 = Payment.objects.create(
            date=date.today(),
            amount=Decimal('500.00'),
            method='EFECTIVO',
            status='PENDIENTE'
        )
        self.payment1.payment_number = Payment.get_next_payment_number()
        self.payment1.save()

        self.payment2 = Payment.objects.create(
            date=date.today(),
            amount=Decimal('300.00'),
            method='TRANSF',
            bank='BANCO PICHINCHA',
            nro_operation='OP123456',
            status='PENDIENTE'
        )
        self.payment2.payment_number = Payment.get_next_payment_number()
        self.payment2.save()

        self.payment_confirmed = Payment.objects.create(
            date=date.today(),
            amount=Decimal('200.00'),
            method='EFECTIVO',
            status='CONFIRMADO'  # No se puede eliminar
        )
        self.payment_confirmed.payment_number = Payment.get_next_payment_number()
        self.payment_confirmed.save()

        # Crear detalles de pago
        PaymentDetail.objects.create(
            payment=self.payment1,
            invoice=self.invoice,
            amount=Decimal('500.00')
        )

        PaymentDetail.objects.create(
            payment=self.payment2,
            invoice=self.invoice,
            amount=Decimal('300.00')
        )

    def test_delete_multiple_payments_success(self):
        """Test para eliminar múltiples pagos exitosamente"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": [self.payment1.id, self.payment2.id]
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = response.json()
        assert '2 payments deleted successfully' in data['message']
        assert 'deleted_payments' in data
        assert len(data['deleted_payments']) == 2

        # Verificar que los pagos se desactivaron
        self.payment1.refresh_from_db()
        self.payment2.refresh_from_db()
        assert not self.payment1.is_active
        assert not self.payment2.is_active

        # Verificar que los detalles también se desactivaron
        payment_details = PaymentDetail.objects.filter(
            payment__in=[self.payment1, self.payment2]
        )
        for detail in payment_details:
            assert not detail.is_active

    def test_delete_payments_mixed_results(self):
        """Test para eliminar pagos con resultados mixtos"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": [
                self.payment1.id,  # Se puede eliminar
                self.payment_confirmed.id,  # No se puede eliminar (confirmado)
                99999  # No existe
            ]
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 207  # Partial success
        data = response.json()
        assert '1 payments deleted successfully' in data['message']
        assert len(data['deleted_payments']) == 1
        assert len(data['cannot_delete_payments']) == 1
        assert len(data['not_found_payments']) == 1

        # Verificar que solo el pago permitido se eliminó
        self.payment1.refresh_from_db()
        assert not self.payment1.is_active

        # Verificar que el pago confirmado no se eliminó
        self.payment_confirmed.refresh_from_db()
        assert self.payment_confirmed.is_active

    def test_delete_payments_missing_payment_ids(self):
        """Test para eliminar sin proporcionar payment_ids"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {}

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        # El endpoint retorna "No data provided" cuando el JSON está vacío
        # antes de verificar campos específicos
        assert data['error'] == 'No data provided'

    def test_delete_payments_missing_payment_ids_field(self):
        """Test para eliminar con datos pero sin el campo payment_ids"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "other_field": "some_value"
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'payment_ids field is required'

    def test_delete_payments_empty_list(self):
        """Test para eliminar con lista vacía"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": []
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'payment_ids must be a non-empty list'

    def test_delete_payments_invalid_type(self):
        """Test para eliminar con tipo de dato inválido"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": "not a list"
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'payment_ids must be a non-empty list'

    def test_delete_payments_all_not_found(self):
        """Test para eliminar pagos que no existen"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": [99999, 88888]
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400  # No se eliminó ninguno
        data = response.json()
        assert '0 payments deleted successfully' in data['message']
        assert len(data['not_found_payments']) == 2

    def test_delete_payments_all_cannot_delete(self):
        """Test para eliminar pagos que no se pueden eliminar"""
        url = reverse('payment_delete_bulk')
        
        delete_data = {
            "payment_ids": [self.payment_confirmed.id]
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400  # No se eliminó ninguno
        data = response.json()
        assert '0 payments deleted successfully' in data['message']
        assert len(data['cannot_delete_payments']) == 1
        assert 'Cannot delete payment with status: CONFIRMADO' in \
               data['cannot_delete_payments'][0]['reason']

    def test_delete_single_payment_success(self):
        """Test para eliminar un pago específico exitosamente"""
        url = reverse('payment_delete', args=[self.payment1.id])

        response = self.client.delete(url)

        assert response.status_code == 200
        data = response.json()
        assert data['message'] == 'Payment deleted successfully'
        assert data['payment_id'] == self.payment1.id
        assert data['payment_number'] == self.payment1.payment_number

        # Verificar que el pago se desactivó
        self.payment1.refresh_from_db()
        assert not self.payment1.is_active

        # Verificar que los detalles también se desactivaron
        payment_details = PaymentDetail.objects.filter(payment=self.payment1)
        for detail in payment_details:
            assert not detail.is_active

    def test_delete_single_payment_not_found(self):
        """Test para eliminar pago que no existe"""
        url = reverse('payment_delete', args=[99999])

        response = self.client.delete(url)

        assert response.status_code == 404
        data = response.json()
        assert data['error'] == 'Payment not found'

    def test_delete_single_payment_cannot_delete(self):
        """Test para eliminar pago confirmado (no se puede eliminar)"""
        url = reverse('payment_delete', args=[self.payment_confirmed.id])

        response = self.client.delete(url)

        assert response.status_code == 400
        data = response.json()
        assert 'Cannot delete payment with status: CONFIRMADO' in data['error']

        # Verificar que el pago no se eliminó
        self.payment_confirmed.refresh_from_db()
        assert self.payment_confirmed.is_active

    def test_delete_payments_invalid_json(self):
        """Test para eliminar con JSON inválido"""
        url = reverse('payment_delete_bulk')
        
        response = self.client.post(
            url,
            data="invalid json",
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'Invalid JSON'

    def test_delete_payments_empty_body(self):
        """Test para eliminar con body vacío"""
        url = reverse('payment_delete_bulk')
        
        response = self.client.post(
            url,
            data="",
            content_type='application/json'
        )

        assert response.status_code == 400
        data = response.json()
        assert data['error'] == 'No data provided'

    def test_delete_payment_with_rejected_status(self):
        """Test para verificar que no se pueden eliminar pagos rechazados"""
        payment_rejected = Payment.objects.create(
            date=date.today(),
            amount=Decimal('100.00'),
            method='EFECTIVO',
            status='RECHAZADO'
        )
        payment_rejected.payment_number = Payment.get_next_payment_number()
        payment_rejected.save()

        url = reverse('payment_delete', args=[payment_rejected.id])

        response = self.client.delete(url)

        assert response.status_code == 400
        data = response.json()
        assert 'Cannot delete payment with status: RECHAZADO' in data['error']

        # Verificar que el pago no se eliminó
        payment_rejected.refresh_from_db()
        assert payment_rejected.is_active
