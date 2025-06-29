import pytest
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel
from products.models import StockDay, StockDetail
from partners.models import Partner
from datetime import date


@pytest.mark.django_db
class TestStockDetailAPI:

    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @pytest.fixture
    def client_logged(self, user):
        """Fixture para cliente autenticado"""
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner de prueba"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="PROVEEDOR TEST",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )

    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un StockDay de prueba"""
        return StockDay.objects.create(
            date=date.today(),
            is_active=True
        )

    @pytest.fixture
    def stock_detail(self, stock_day, partner):
        """Fixture para crear un StockDetail de prueba"""
        return StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            quantity=10,
            box_model="HB",
            tot_stem_flower=250,
            tot_cost_price_box=15.50
        )

    def test_get_stock_detail_success(
        self, client_logged, stock_detail
    ):
        """Test para obtener stock detail exitosamente"""
        url = reverse('stock_detail', args=[stock_detail.stock_day.id])
        response = client_logged.get(url)

        assert response.status_code == 200

        data = response.json()
        assert 'stock' in data
        assert 'stockDay' in data
        assert 'orders' in data

        # Verificar estructura de stockDay
        stock_day_data = data['stockDay']
        assert 'id' in stock_day_data
        assert 'date' in stock_day_data
        assert 'is_active' in stock_day_data
        assert stock_day_data['id'] == stock_detail.stock_day.id

        # Verificar que hay stock data
        assert isinstance(data['stock'], list)
        assert len(data['stock']) >= 1

        # Verificar que orders es una lista
        assert isinstance(data['orders'], list)

    def test_get_stock_detail_not_found(self, client_logged):
        """Test para stock day que no existe"""
        url = reverse('stock_detail', args=[99999])

        # Nota: La API actualmente lanza Exception en lugar de devolver 404
        # El comportamiento actual es error 500, no 404
        with pytest.raises(Exception, match="Registro de stock Eliminado"):
            client_logged.get(url)

    def test_get_stock_detail_empty(self, client_logged, stock_day):
        """Test para stock day sin detalles"""
        url = reverse('stock_detail', args=[stock_day.id])
        response = client_logged.get(url)

        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
        assert 'No hay detalles para esta diponibilidad' in data['error']

    def test_stock_detail_response_format(
        self, client_logged, stock_detail
    ):
        """Test para verificar el formato de respuesta"""
        url = reverse('stock_detail', args=[stock_detail.stock_day.id])
        response = client_logged.get(url)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

        data = response.json()
        assert isinstance(data, dict)

        # Verificar tipos de cada campo
        assert isinstance(data['stock'], list)
        assert isinstance(data['stockDay'], dict)
        assert isinstance(data['orders'], list)
