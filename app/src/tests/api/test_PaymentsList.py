import json
import pytest
from django.urls import reverse
from django.test import Client
from datetime import date, timedelta
from decimal import Decimal
from common.AppLoger import loggin_event
from trade.models.Payment import Payment
from trade.models.Invoice import Invoice
from partners.models.Partner import Partner
from accounts.models import CustomUserModel
from tests.BaseViewTest import BaseViewTest


@pytest.mark.django_db
class TestPaymentsListAPI(BaseViewTest):

    @pytest.fixture
    def url(self):
        return reverse('payments_list_api')  # Ajustar según tu URLconf

    @pytest.fixture
    def test_data(self):
        """Crear datos de prueba"""
        # Crear partner proveedor
        supplier = Partner.objects.create(
            business_tax_id='123456789',
            name='Proveedor Test',
            short_name='PROV_TEST',
            address='Dirección Test',
            country='Ecuador',
            city='Quito',
            type_partner='PROVEEDOR'
        )

        # Crear facturas de compra
        invoice1 = Invoice.objects.create(
            partner=supplier,
            num_invoice='FAC-001',
            type_document='FAC_COMPRA',
            total_price=Decimal('1000.00'),
            status='PENDIENTE'
        )

        invoice2 = Invoice.objects.create(
            partner=supplier,
            num_invoice='FAC-002',
            type_document='FAC_COMPRA',
            total_price=Decimal('500.00'),
            status='PENDIENTE'
        )

        # Crear pagos (egresos)
        today = date.today()

        payment1 = Payment.objects.create(
            date=today,
            due_date=today + timedelta(days=30),
            type_transaction='EGRESO',
            amount=Decimal('1000.00'),
            method='TRANSF',
            status='CONFIRMADO',
            bank='Banco Test',
            nro_operation='OP123456'
        )
        payment1.invoices.add(invoice1)

        payment2 = Payment.objects.create(
            date=today - timedelta(days=5),
            due_date=today - timedelta(days=1),  # Vencido
            type_transaction='EGRESO',
            amount=Decimal('500.00'),
            method='CHEQUE',
            status='PENDIENTE'
        )
        payment2.invoices.add(invoice2)

        # Crear pago de ingreso (no debe aparecer en payments)
        payment_ingreso = Payment.objects.create(
            date=today,
            type_transaction='INGRESO',
            amount=Decimal('2000.00'),
            method='EFECTIVO',
            status='CONFIRMADO'
        )

        return {
            'supplier': supplier,
            'invoices': [invoice1, invoice2],
            'payments': [payment1, payment2],
            'payment_ingreso': payment_ingreso
        }

    def test_get_all_payments(self, client_logged, url, test_data):
        """Test obtener todos los pagos realizados"""
        loggin_event('[TEST] Test obtener todos los pagos realizados')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['total_records'] == 2  # Solo egresos
        assert len(data['data']) == 2

        # Verificar estructura de datos
        payment_data = data['data'][0]
        assert 'id' in payment_data
        assert 'payment_number' in payment_data
        assert 'amount' in payment_data
        assert 'method' in payment_data
        assert 'status' in payment_data
        assert 'invoices' in payment_data
        assert 'partners' in payment_data
        assert 'is_overdue' in payment_data

    def test_filter_by_status(self, client_logged, url, test_data):
        """Test filtrar pagos por estado"""
        loggin_event('[TEST] Test filtrar pagos por estado')

        response = client_logged.get(url + '?status=CONFIRMADO')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['status'] == 'CONFIRMADO'

    def test_filter_by_partner(self, client_logged, url, test_data):
        """Test filtrar pagos por partner"""
        loggin_event('[TEST] Test filtrar pagos por partner')

        partner_id = test_data['supplier'].id
        response = client_logged.get(url + f'?partner_id={partner_id}')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 2

        # Verificar que todos los pagos son del partner correcto
        for payment in data['data']:
            partner_found = False
            for partner in payment['partners']:
                if partner['id'] == partner_id:
                    partner_found = True
                    break
            assert partner_found

    def test_filter_by_date_range(self, client_logged, url, test_data):
        """Test filtrar pagos por rango de fechas"""
        loggin_event('[TEST] Test filtrar pagos por rango de fechas')

        today = date.today()
        date_from = today.isoformat()
        date_to = today.isoformat()

        response = client_logged.get(
            url + f'?date_from={date_from}&date_to={date_to}')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1  # Solo el pago de hoy

    def test_filter_by_method(self, client_logged, url, test_data):
        """Test filtrar pagos por método"""
        loggin_event('[TEST] Test filtrar pagos por método')

        response = client_logged.get(url + '?method=TRANSF')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['method'] == 'TRANSF'

    def test_filter_overdue_only(self, client_logged, url, test_data):
        """Test filtrar solo pagos vencidos"""
        loggin_event('[TEST] Test filtrar solo pagos vencidos')

        response = client_logged.get(url + '?overdue_only=true')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['is_overdue'] is True
        assert data['data'][0]['status'] == 'PENDIENTE'

    def test_statistics_calculation(self, client_logged, url, test_data):
        """Test cálculo de estadísticas"""
        loggin_event('[TEST] Test cálculo de estadísticas de pagos')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200
        assert 'statistics' in data

        stats = data['statistics']
        assert 'payments' in stats
        assert 'invoices' in stats

        # Verificar estadísticas de pagos
        payment_stats = stats['payments']
        assert payment_stats['total_confirmed_amount'] == 1000.0
        assert payment_stats['total_pending_amount'] == 500.0
        assert payment_stats['count_confirmed'] == 1
        assert payment_stats['count_pending'] == 1
        assert payment_stats['total_overdue_amount'] == 500.0
        assert payment_stats['count_overdue'] == 1

    def test_invalid_date_format(self, client_logged, url, test_data):
        """Test con formato de fecha inválido"""
        loggin_event('[TEST] Test con formato de fecha inválido')

        response = client_logged.get(url + '?date_from=invalid-date')

        # Debe seguir funcionando ignorando la fecha inválida
        assert response.status_code == 200

    def test_empty_results(self, client_logged, url, test_data):
        """Test con filtros que no devuelven resultados"""
        loggin_event('[TEST] Test con filtros sin resultados')

        response = client_logged.get(url + '?status=INEXISTENTE')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 0
        assert len(data['data']) == 0

    def test_combined_filters(self, client_logged, url, test_data):
        """Test combinando múltiples filtros"""
        loggin_event('[TEST] Test combinando múltiples filtros')

        today = date.today()
        partner_id = test_data['supplier'].id

        response = client_logged.get(
            url + f'?status=CONFIRMADO&partner_id={partner_id}&method=TRANSF'
        )
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1

        payment = data['data'][0]
        assert payment['status'] == 'CONFIRMADO'
        assert payment['method'] == 'TRANSF'

    def test_ordering(self, client_logged, url, test_data):
        """Test que los resultados estén ordenados por fecha descendente"""
        loggin_event('[TEST] Test ordenamiento por fecha descendente')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200

        if len(data['data']) > 1:
            # Verificar que están ordenados por fecha descendente
            dates = [payment['date'] for payment in data['data']]
            assert dates == sorted(dates, reverse=True)

    def test_payment_display_data(self, client_logged, url, test_data):
        """Test que los datos de display se muestren correctamente"""
        loggin_event('[TEST] Test datos de display de pagos')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200

        payment = data['data'][0]
        assert 'method_display' in payment
        assert 'status_display' in payment

        # Verificar que los displays no estén vacíos
        assert payment['method_display'] != ''
        assert payment['status_display'] != ''
