import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import CustomUserModel
from partners.models import Partner, Contact
from products.models import StockDay
from datetime import date


@pytest.mark.django_db
class TestAllSuppliersAPI:

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
    def suppliers(self):
        """Fixture para crear proveedores de prueba"""
        suppliers = []
        for i in range(2):
            supplier = Partner.objects.create(
                business_tax_id=f"987654321{i}",
                name=f"PROVEEDOR {i+1}",
                address=f"Av. Proveedor {i+1}",
                country="Ecuador",
                city="Quito",
                type_partner="PROVEEDOR"
            )
            # Crear contacto principal para cada proveedor
            Contact.objects.create(
                partner=supplier,
                name=f"Contacto Proveedor {i+1}",
                contact_type="PRINCIPAL",
                email=f"proveedor{i+1}@test.com",
                phone=f"098765432{i}"
            )
            suppliers.append(supplier)
        return suppliers

    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un StockDay de prueba"""
        return StockDay.objects.create(
            date=date.today(),
            is_active=True
        )

    @pytest.fixture
    def url(self):
        """URL del endpoint"""
        return reverse('all_supliers')

    def test_get_all_suppliers_success_without_stock(
        self, client_logged, url, suppliers
    ):
        """Test para obtener todos los proveedores sin stock"""
        response = client_logged.get(url, {'id_stock': '0'})

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # Verificar que hay al menos nuestros proveedores creados
        assert len(data) >= 2

        # Verificar estructura de cada proveedor
        for supplier_data in data:
            assert 'id' in supplier_data
            assert 'name' in supplier_data
            assert 'short_name' in supplier_data
            assert 'business_tax_id' in supplier_data
            assert 'address' in supplier_data
            assert 'city' in supplier_data
            assert 'is_active' in supplier_data
            assert 'contact' in supplier_data
            assert 'related_partners' in supplier_data
            assert 'have_stock' in supplier_data
            assert 'is_selected' in supplier_data
            # have_stock debe ser False cuando id_stock es '0'
            assert supplier_data['have_stock'] is False

    def test_get_all_suppliers_success_with_stock(
        self, client_logged, url, suppliers, stock_day
    ):
        """Test para obtener todos los proveedores con stock"""
        response = client_logged.get(url, {'id_stock': str(stock_day.id)})

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # Verificar que hay al menos nuestros proveedores creados
        assert len(data) >= 2

        # Verificar estructura
        for supplier_data in data:
            assert 'have_stock' in supplier_data
            # have_stock puede ser True o False dependiendo de si hay stock
            assert isinstance(supplier_data['have_stock'], bool)

    def test_get_suppliers_missing_id_stock(self, client_logged, url):
        """Test para proveedores sin parámetro id_stock"""
        response = client_logged.get(url)

        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
        assert 'ID de stock no proporcionado' in data['error']

    def test_suppliers_response_format(self, client_logged, url):
        """Test para verificar el formato de respuesta"""
        response = client_logged.get(url, {'id_stock': '0'})

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

        data = response.json()
        assert isinstance(data, list)

    def test_supplier_contact_structure(
        self, client_logged, url, suppliers
    ):
        """Test para verificar la estructura del contacto en la respuesta"""
        response = client_logged.get(url, {'id_stock': '0'})
        data = response.json()

        # Buscar nuestros proveedores creados en la respuesta
        created_supplier_names = [s.name for s in suppliers]
        found_suppliers = [
            s for s in data
            if s['name'] in created_supplier_names
        ]

        # Verificar que encontramos al menos uno de nuestros proveedores
        assert len(found_suppliers) >= 1

        # Verificar estructura del contacto
        first_supplier = found_suppliers[0]
        if first_supplier['contact']:  # Si tiene contacto
            contact = first_supplier['contact']
            assert 'name' in contact
            assert 'email' in contact
            assert 'phone' in contact
            assert 'contact_type' in contact
            assert 'position' in contact
            assert 'is_principal' in contact

    def test_supplier_has_related_partners_list(
        self, client_logged, url, suppliers
    ):
        """Test para verificar que cada proveedor tiene lista de
        related_partners"""
        response = client_logged.get(url, {'id_stock': '0'})
        data = response.json()

        for supplier in data:
            assert 'related_partners' in supplier
            assert isinstance(supplier['related_partners'], list)

    def test_suppliers_data_fields(self, client_logged, url, suppliers):
        """Test para verificar que los campos específicos están presentes"""
        response = client_logged.get(url, {'id_stock': '0'})
        data = response.json()

        if data:  # Si hay proveedores
            first_supplier = data[0]

            # Campos requeridos según la API real
            required_fields = [
                'id', 'name', 'short_name', 'business_tax_id', 'address',
                'city', 'website', 'credit_term', 'is_profit_margin_included',
                'default_profit_margin', 'consolidate', 'skype', 'email',
                'phone', 'is_active', 'contact', 'is_selected', 'have_stock',
                'related_partners'
            ]

            for field in required_fields:
                assert field in first_supplier
