import pytest
from django.test import Client
from django.urls import reverse
from accounts.models import CustomUserModel
from partners.models import Partner, Contact


@pytest.mark.django_db
class TestAllCustomerAPI:

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
    def customers(self):
        """Fixture para crear clientes de prueba"""
        customers = []
        for i in range(2):
            customer = Partner.objects.create(
                business_tax_id=f"123456789{i}",
                name=f"CLIENTE {i+1}",
                address=f"Av. Test {i+1}",
                country="Ecuador",
                city="Quito",
                type_partner="CLIENTE"
            )
            # Crear contacto principal para cada cliente
            Contact.objects.create(
                partner=customer,
                name=f"Contacto {i+1}",
                contact_type="PRINCIPAL",
                email=f"contacto{i+1}@test.com",
                phone=f"098765432{i}"
            )
            customers.append(customer)
        return customers

    @pytest.fixture
    def url(self):
        """URL del endpoint"""
        return reverse('all_customers')

    def test_get_all_customers_success(self, client_logged, url, customers):
        """Test para obtener todos los clientes exitosamente"""
        response = client_logged.get(url)

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        # Verificar que hay al menos nuestros clientes creados
        assert len(data) >= 2

        # Verificar estructura de cada cliente
        for customer_data in data:
            assert 'id' in customer_data
            assert 'name' in customer_data
            assert 'business_tax_id' in customer_data
            assert 'country' in customer_data
            assert 'city' in customer_data
            assert 'is_active' in customer_data
            assert 'contact' in customer_data
            assert 'related_partners' in customer_data

    def test_get_all_customers_response_format(self, client_logged, url):
        """Test para verificar el formato de respuesta"""
        response = client_logged.get(url)

        assert response.status_code == 200
        assert response['Content-Type'] == 'application/json'

        data = response.json()
        assert isinstance(data, list)

    def test_customer_contact_structure(self, client_logged, url, customers):
        """Test para verificar la estructura del contacto en la respuesta"""
        response = client_logged.get(url)
        data = response.json()

        # Buscar nuestros clientes creados en la respuesta
        created_customer_names = [c.name for c in customers]
        found_customers = [
            c for c in data
            if c['name'] in created_customer_names
        ]

        # Verificar que encontramos al menos uno de nuestros clientes
        assert len(found_customers) >= 1

        # Verificar estructura del contacto
        first_customer = found_customers[0]
        if first_customer['contact']:  # Si tiene contacto
            contact = first_customer['contact']
            assert 'name' in contact
            assert 'email' in contact
            assert 'phone' in contact
            assert 'contact_type' in contact

    def test_customer_has_related_partners_list(
        self, client_logged, url, customers
    ):
        """Test para verificar que cada cliente tiene lista de
        related_partners"""
        response = client_logged.get(url)
        data = response.json()

        for customer in data:
            assert 'related_partners' in customer
            assert isinstance(customer['related_partners'], list)

    def test_customers_data_fields(self, client_logged, url, customers):
        """Test para verificar que los campos específicos están presentes"""
        response = client_logged.get(url)
        data = response.json()

        if data:  # Si hay clientes
            first_customer = data[0]

            # Campos requeridos según la API real
            required_fields = [
                'id', 'name', 'business_tax_id', 'address',
                'country', 'city', 'website', 'credit_term',
                'consolidate', 'skype', 'email', 'phone', 'is_active',
                'contact', 'related_partners', 'is_selected'
            ]

            for field in required_fields:
                assert field in first_customer
