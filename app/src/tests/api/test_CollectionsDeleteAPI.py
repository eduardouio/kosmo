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
class TestCollectionsDeleteAPI:

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

    def test_delete_collection_success(self):
        """Test para eliminar un cobro exitosamente"""
        # Crear un cobro pendiente
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='COL-000001'
        )

        detail = PaymentDetail.objects.create(
            payment=collection,
            invoice=self.invoice,
            amount=Decimal('1000.00')
        )

        url = reverse('collection_delete', kwargs={
                      'collection_id': collection.id})

        response = self.client.delete(url)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'COL-000001 eliminado exitosamente' in data['message']

        # Verificar soft delete
        collection.refresh_from_db()
        assert collection.is_active is False

        detail.refresh_from_db()
        assert detail.is_active is False

    def test_delete_collection_not_found(self):
        """Test para intentar eliminar un cobro inexistente"""
        url = reverse('collection_delete', kwargs={'collection_id': 99999})

        response = self.client.delete(url)

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Cobro no encontrado' in data['error']

    def test_delete_confirmed_collection_fails(self):
        """Test para verificar que no se pueden eliminar cobros confirmados"""
        # Crear un cobro confirmado
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='CONFIRMADO',  # Estado confirmado
            payment_number='COL-000001'
        )

        url = reverse('collection_delete', kwargs={
                      'collection_id': collection.id})

        response = self.client.delete(url)

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'No se puede eliminar un cobro confirmado' in data['error']

        # Verificar que el cobro NO fue eliminado
        collection.refresh_from_db()
        assert collection.is_active is True

    def test_delete_multiple_collections_success(self):
        """Test para eliminar múltiples cobros exitosamente"""
        # Crear varios cobros pendientes
        collection1 = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='COL-000001'
        )

        collection2 = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1500.00'),
            method='TRANSF',
            status='PENDIENTE',
            payment_number='COL-000002'
        )

        collection3 = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('2000.00'),
            method='CHEQUE',
            status='CONFIRMADO',  # Este no se debería eliminar
            payment_number='COL-000003'
        )

        url = reverse('collection_delete_bulk')

        delete_data = {
            "collection_ids": [collection1.id, collection2.id, collection3.id]
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True
        assert 'Proceso de eliminación completado' in data['message']

        # Verificar el resumen
        assert data['summary']['total_requested'] == 3
        assert data['summary']['successfully_deleted'] == 2
        assert data['summary']['errors_count'] == 1

        # Verificar eliminaciones
        collection1.refresh_from_db()
        assert collection1.is_active is False

        collection2.refresh_from_db()
        assert collection2.is_active is False

        collection3.refresh_from_db()
        assert collection3.is_active is True  # No eliminado por estar confirmado

        # Verificar errores
        assert len(data['errors']) == 1
        assert data['errors'][0]['collection_id'] == collection3.id
        assert 'está confirmado' in data['errors'][0]['error']

    def test_delete_multiple_collections_no_ids(self):
        """Test para validar que se requieren IDs en eliminación múltiple"""
        url = reverse('collection_delete_bulk')

        delete_data = {
            "collection_ids": []
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Debe proporcionar al menos un ID de cobro' in data['error']

    def test_delete_multiple_collections_missing_field(self):
        """Test para validar campo requerido en eliminación múltiple"""
        url = reverse('collection_delete_bulk')

        delete_data = {}  # Sin collection_ids

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Debe proporcionar al menos un ID de cobro' in data['error']

    def test_delete_multiple_collections_with_nonexistent_ids(self):
        """Test para manejar IDs de cobros inexistentes en eliminación múltiple"""
        # Crear un cobro válido
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='COL-000001'
        )

        url = reverse('collection_delete_bulk')

        delete_data = {
            "collection_ids": [collection.id, 99999, 88888]  # IDs inexistentes
        }

        response = self.client.post(
            url,
            data=json.dumps(delete_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data['success'] is True

        # Verificar el resumen
        assert data['summary']['total_requested'] == 3
        assert data['summary']['successfully_deleted'] == 1
        assert data['summary']['errors_count'] == 2

        # Verificar que el cobro válido fue eliminado
        collection.refresh_from_db()
        assert collection.is_active is False

        # Verificar errores por IDs inexistentes
        assert len(data['errors']) == 2
        error_ids = [error['collection_id'] for error in data['errors']]
        assert 99999 in error_ids
        assert 88888 in error_ids

    def test_delete_collection_only_affects_ingreso_type(self):
        """Test para verificar que solo afecta cobros (INGRESO) y no pagos (EGRESO)"""
        # Crear un pago (EGRESO) con el mismo ID que podría confundirse
        payment = Payment.objects.create(
            date=date.today(),
            type_transaction='EGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='PAY-000001'
        )

        # Crear un cobro (INGRESO)
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='COL-000001'
        )

        # Intentar eliminar usando el ID del pago en el endpoint de cobros
        url = reverse('collection_delete', kwargs={
                      'collection_id': payment.id})

        response = self.client.delete(url)

        assert response.status_code == 404
        data = json.loads(response.content)
        assert data['success'] is False
        assert 'Cobro no encontrado' in data['error']

        # Verificar que el pago NO fue afectado
        payment.refresh_from_db()
        assert payment.is_active is True

        # Ahora eliminar el cobro correctamente
        url = reverse('collection_delete', kwargs={
                      'collection_id': collection.id})
        response = self.client.delete(url)

        assert response.status_code == 200
        collection.refresh_from_db()
        assert collection.is_active is False

    def test_delete_collection_with_details_cascade(self):
        """Test para verificar que se eliminan los detalles en cascada"""
        # Crear un cobro con múltiples detalles
        collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('1000.00'),
            method='EFECTIVO',
            status='PENDIENTE',
            payment_number='COL-000001'
        )

        # Crear segunda factura
        invoice2 = Invoice.objects.create(
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

        detail1 = PaymentDetail.objects.create(
            payment=collection,
            invoice=self.invoice,
            amount=Decimal('600.00')
        )

        detail2 = PaymentDetail.objects.create(
            payment=collection,
            invoice=invoice2,
            amount=Decimal('400.00')
        )

        url = reverse('collection_delete', kwargs={
                      'collection_id': collection.id})

        response = self.client.delete(url)

        assert response.status_code == 200

        # Verificar que todos los detalles fueron marcados como inactivos
        detail1.refresh_from_db()
        assert detail1.is_active is False

        detail2.refresh_from_db()
        assert detail2.is_active is False

    def test_delete_collection_invalid_json(self):
        """Test para manejar JSON inválido en eliminación múltiple"""
        url = reverse('collection_delete_bulk')

        response = self.client.post(
            url,
            data='{"invalid": json}',  # JSON malformado
            content_type='application/json'
        )

        assert response.status_code == 400
        data = json.loads(response.content)
        assert 'Invalid JSON format' in data['error']

    def test_delete_collection_no_body(self):
        """Test para manejar request sin body en eliminación múltiple"""
        url = reverse('collection_delete_bulk')

        response = self.client.post(url)

        assert response.status_code == 400
        data = json.loads(response.content)
        assert 'No data provided' in data['error']
