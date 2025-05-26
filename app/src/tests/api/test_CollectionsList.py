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
class TestCollectionsListAPI(BaseViewTest):

    @pytest.fixture
    def url(self):
        return reverse('collections_list_api')  # Ajustar según tu URLconf

    @pytest.fixture
    def test_data(self):
        """Crear datos de prueba para cobros"""
        # Crear partner cliente
        customer = Partner.objects.create(
            business_tax_id='987654321',
            name='Cliente Test',
            short_name='CLI_TEST',
            address='Dirección Cliente',
            country='USA',
            city='Miami',
            type_partner='CLIENTE'
        )

        # Crear facturas de venta
        invoice1 = Invoice.objects.create(
            partner=customer,
            num_invoice='FV-001',
            type_document='FAC_VENTA',
            total_price=Decimal('2000.00'),
            total_margin=Decimal('200.00'),
            status='PENDIENTE'
        )

        invoice2 = Invoice.objects.create(
            partner=customer,
            num_invoice='FV-002',
            type_document='FAC_VENTA',
            total_price=Decimal('1500.00'),
            total_margin=Decimal('150.00'),
            status='PENDIENTE'
        )

        # Crear cobros (ingresos)
        today = date.today()

        collection1 = Payment.objects.create(
            date=today,
            due_date=today + timedelta(days=30),
            type_transaction='INGRESO',
            amount=Decimal('2200.00'),  # total_price + total_margin
            method='TC',
            status='CONFIRMADO',
            bank='Banco Cliente',
            nro_operation='TC789012'
        )
        collection1.invoices.add(invoice1)

        collection2 = Payment.objects.create(
            date=today - timedelta(days=10),
            due_date=today - timedelta(days=2),  # Vencido
            type_transaction='INGRESO',
            amount=Decimal('1650.00'),
            method='TRANSF',
            status='PENDIENTE',
            bank='Banco Internacional'
        )
        collection2.invoices.add(invoice2)

        # Crear pago de egreso (no debe aparecer en collections)
        payment_egreso = Payment.objects.create(
            date=today,
            type_transaction='EGRESO',
            amount=Decimal('800.00'),
            method='EFECTIVO',
            status='CONFIRMADO'
        )

        return {
            'customer': customer,
            'invoices': [invoice1, invoice2],
            'collections': [collection1, collection2],
            'payment_egreso': payment_egreso
        }

    def test_get_all_collections(self, client_logged, url, test_data):
        """Test obtener todos los cobros recibidos"""
        loggin_event('[TEST] Test obtener todos los cobros recibidos')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200
        assert data['success'] is True
        assert data['total_records'] == 2  # Solo ingresos
        assert len(data['data']) == 2

        # Verificar estructura de datos
        collection_data = data['data'][0]
        assert 'id' in collection_data
        assert 'payment_number' in collection_data
        assert 'amount' in collection_data
        assert 'method' in collection_data
        assert 'status' in collection_data
        assert 'invoices' in collection_data
        assert 'partners' in collection_data
        assert 'is_overdue' in collection_data

    def test_filter_by_status_collections(self, client_logged, url, test_data):
        """Test filtrar cobros por estado"""
        loggin_event('[TEST] Test filtrar cobros por estado')

        response = client_logged.get(url + '?status=CONFIRMADO')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['status'] == 'CONFIRMADO'

    def test_filter_by_customer(self, client_logged, url, test_data):
        """Test filtrar cobros por cliente"""
        loggin_event('[TEST] Test filtrar cobros por cliente')

        customer_id = test_data['customer'].id
        response = client_logged.get(url + f'?partner_id={customer_id}')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 2

        # Verificar que todos los cobros son del cliente correcto
        for collection in data['data']:
            partner_found = False
            for partner in collection['partners']:
                if partner['id'] == customer_id:
                    partner_found = True
                    break
            assert partner_found

    def test_filter_overdue_collections(self, client_logged, url, test_data):
        """Test filtrar solo cobros vencidos"""
        loggin_event('[TEST] Test filtrar solo cobros vencidos')

        response = client_logged.get(url + '?overdue_only=true')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['is_overdue'] is True
        assert data['data'][0]['status'] == 'PENDIENTE'

    def test_collections_statistics(self, client_logged, url, test_data):
        """Test cálculo de estadísticas de cobros"""
        loggin_event('[TEST] Test cálculo de estadísticas de cobros')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200
        assert 'statistics' in data

        stats = data['statistics']
        assert 'collections' in stats
        assert 'invoices' in stats

        # Verificar estadísticas de cobros
        collection_stats = stats['collections']
        assert collection_stats['total_confirmed_amount'] == 2200.0
        assert collection_stats['total_pending_amount'] == 1650.0
        assert collection_stats['count_confirmed'] == 1
        assert collection_stats['count_pending'] == 1
        assert collection_stats['total_overdue_amount'] == 1650.0
        assert collection_stats['count_overdue'] == 1

    def test_invoice_totals_in_collections(self, client_logged, url, test_data):
        """Test que los totales de facturas incluyan margen en ventas"""
        loggin_event('[TEST] Test totales de facturas con margen en cobros')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200

        # Buscar el cobro confirmado
        confirmed_collection = None
        for collection in data['data']:
            if collection['status'] == 'CONFIRMADO':
                confirmed_collection = collection
                break

        assert confirmed_collection is not None

        # Verificar que el total de la factura incluye el margen
        invoice_info = confirmed_collection['invoices'][0]
        assert invoice_info['total'] == 2200.0  # total_price + total_margin

    def test_multiple_invoices_per_collection(self, client_logged, url, test_data):
        """Test cobro asociado a múltiples facturas"""
        loggin_event('[TEST] Test cobro con múltiples facturas')

        # Crear un cobro que cubra ambas facturas
        customer = test_data['customer']
        invoice1, invoice2 = test_data['invoices']

        multi_collection = Payment.objects.create(
            date=date.today(),
            type_transaction='INGRESO',
            amount=Decimal('3850.00'),  # Total de ambas facturas
            method='TRANSF',
            status='CONFIRMADO'
        )
        multi_collection.invoices.add(invoice1, invoice2)

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 3  # Los 2 originales + el nuevo

        # Buscar el cobro con múltiples facturas
        multi_payment = None
        for collection in data['data']:
            if len(collection['invoices']) == 2:
                multi_payment = collection
                break

        assert multi_payment is not None
        assert len(multi_payment['invoices']) == 2
        assert multi_payment['total_invoices_amount'] == 3850.0

    def test_collections_date_range_filter(self, client_logged, url, test_data):
        """Test filtro por rango de fechas en cobros"""
        loggin_event('[TEST] Test filtro por rango de fechas en cobros')

        today = date.today()
        yesterday = today - timedelta(days=1)

        # Filtrar solo cobros de ayer hacia atrás
        response = client_logged.get(url + f'?date_to={yesterday.isoformat()}')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1  # Solo el cobro de hace 10 días

    def test_collections_method_filter(self, client_logged, url, test_data):
        """Test filtro por método de pago en cobros"""
        loggin_event('[TEST] Test filtro por método de pago en cobros')

        response = client_logged.get(url + '?method=TC')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 1
        assert data['data'][0]['method'] == 'TC'
        assert data['data'][0]['method_display'] == 'TARJETA DE CRÉDITO'

    def test_collections_error_handling(self, client_logged, url, test_data):
        """Test manejo de errores en cobros"""
        loggin_event('[TEST] Test manejo de errores en API de cobros')

        # Test con filtros inválidos (debe funcionar normalmente)
        response = client_logged.get(url + '?partner_id=99999')
        data = response.json()

        assert response.status_code == 200
        assert data['total_records'] == 0

    def test_collections_sorting(self, client_logged, url, test_data):
        """Test ordenamiento de cobros por fecha"""
        loggin_event('[TEST] Test ordenamiento de cobros por fecha')

        response = client_logged.get(url)
        data = response.json()

        assert response.status_code == 200

        if len(data['data']) > 1:
            # Verificar ordenamiento por fecha descendente
            dates = [collection['date'] for collection in data['data']]
            assert dates == sorted(dates, reverse=True)
