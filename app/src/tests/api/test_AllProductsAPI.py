import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import CustomUserModel
from products.models import Product


@pytest.mark.django_db
class TestAllProductsAPI:

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
    def products(self):
        """Fixture para crear productos de prueba"""
        products = []
        for i in range(3):
            product = Product.objects.create(
                name=f"Producto {i+1}",
                variety=f"VARIEDAD_{i+1}",
                colors=f"Color {i+1}",
                default_profit_margin=0.20 + (i * 0.05)
            )
            products.append(product)
        return products

    @pytest.fixture
    def url(self):
        """URL del endpoint"""
        return reverse('all_products')

    def test_get_all_products_success(self, client_logged, url, products):
        """Test para obtener todos los productos exitosamente"""
        response = client_logged.get(url)

        assert response.status_code == 200

        data = response.json()
        assert 'products' in data
        # Verificar que hay al menos nuestros 3 productos creados
        assert len(data['products']) >= 3

        # Verificar estructura de cada producto
        for product_data in data['products']:
            assert 'id' in product_data
            assert 'name' in product_data
            assert 'variety' in product_data
            assert 'image' in product_data
            assert 'colors' in product_data
            assert 'default_profit_margin' in product_data

    def test_get_all_products_not_empty(self, client_logged, url):
        """Test cuando hay productos en la base de datos"""
        response = client_logged.get(url)

        assert response.status_code == 200
        data = response.json()
        assert 'products' in data
        # La BD tiene productos existentes, no debería estar vacía
        assert len(data['products']) > 0

    def test_get_all_products_data_structure(
        self, client_logged, url, products
    ):
        """Test para verificar la estructura de datos específica"""
        response = client_logged.get(url)
        data = response.json()

        # Buscar nuestros productos creados en la respuesta
        created_product_names = [p.name for p in products]
        found_products = [
            p for p in data['products']
            if p['name'] in created_product_names
        ]

        # Verificar que encontramos al menos uno de nuestros productos
        assert len(found_products) >= 1

        # Verificar estructura del primer producto encontrado
        first_found = found_products[0]
        assert 'id' in first_found
        assert 'name' in first_found
        assert 'variety' in first_found
        assert 'colors' in first_found
        assert 'default_profit_margin' in first_found
        assert 'image' in first_found

    def test_response_format(self, client_logged, url, products):
        """Test para verificar el formato de respuesta"""
        response = client_logged.get(url)

        assert response['Content-Type'] == 'application/json'
        assert response.status_code == 200

        # Verificar que es un JSON válido
        data = response.json()
        assert isinstance(data, dict)
        assert isinstance(data['products'], list)
