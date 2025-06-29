import pytest
from django.db import IntegrityError
from partners.models import Contact, Partner


@pytest.mark.django_db
class TestContact:
    
    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )
        
    def test_create_contact(self, partner):
        """Test creación de contacto"""
        contact = Contact.objects.create(
            partner=partner,
            name="juan perez",
            position="gerente",
            contact_type="GERENCIA",
            phone="123456789",
            email="juan@test.com",
            is_principal=True
        )
        assert contact.name == "JUAN PEREZ"
        assert contact.position == "GERENTE"
        assert contact.phone == "123456789"
        assert contact.contact_type == "GERENCIA"
        assert contact.email == "juan@test.com"
        assert contact.is_principal is True
        
    def test_uppercase_conversion(self, partner):
        """Test conversión a mayúsculas en save"""
        contact = Contact.objects.create(
            partner=partner,
            name="maría gonzález",
            position="vendedora",
            phone="987654321"
        )
        assert contact.name == "MARÍA GONZÁLEZ"
        assert contact.position == "VENDEDORA"
        assert contact.phone == "987654321"
        
    def test_contact_type_choices(self, partner):
        """Test choices de tipo de contacto"""
        contact_types = ['COMERCIAL', 'FINANCIERO', 'LOGISTICA', 'GERENCIA', 'OTRO']
        
        for contact_type in contact_types:
            contact = Contact.objects.create(
                partner=partner,
                name=f"Contact {contact_type}",
                contact_type=contact_type
            )
            assert contact.contact_type == contact_type
            
    def test_default_contact_type(self, partner):
        """Test tipo de contacto por defecto"""
        contact = Contact.objects.create(
            partner=partner,
            name="Test Contact"
        )
        assert contact.contact_type == "COMERCIAL"
        
    def test_unique_together_constraint(self, partner):
        """Test restricción unique_together de partner y name"""
        Contact.objects.create(
            partner=partner,
            name="Test Contact"
        )
        with pytest.raises(IntegrityError):
            Contact.objects.create(
                partner=partner,
                name="Test Contact"
            )
            
    def test_get_by_partner(self, partner):
        """Test método classmethod get_by_partner"""
        contact1 = Contact.objects.create(
            partner=partner,
            name="Contact 1"
        )
        contact2 = Contact.objects.create(
            partner=partner,
            name="Contact 2"
        )
        
        contacts = Contact.get_by_partner(partner)
        assert contact1 in contacts
        assert contact2 in contacts
        assert contacts.count() == 2
        
    def test_get_principal_by_partner(self, partner):
        """Test método classmethod get_principal_by_partner"""
        contact1 = Contact.objects.create(
            partner=partner,
            name="Contact 1",
            is_principal=False
        )
        contact2 = Contact.objects.create(
            partner=partner,
            name="Contact 2",
            is_principal=True
        )
        
        principal = Contact.get_principal_by_partner(partner)
        assert principal == contact2
        assert principal.is_principal is True
        
    def test_get_principal_by_partner_none(self, partner):
        """Test get_principal_by_partner cuando no hay principal"""
        Contact.objects.create(
            partner=partner,
            name="Contact 1",
            is_principal=False
        )
        
        principal = Contact.get_principal_by_partner(partner)
        assert principal is None
        
    def test_str_method(self, partner):
        """Test método __str__"""
        contact = Contact.objects.create(
            partner=partner,
            name="Test Contact"
        )
        assert str(contact) == "TEST CONTACT"
        
    def test_optional_fields(self, partner):
        """Test campos opcionales"""
        contact = Contact.objects.create(
            partner=partner,
            name="Test Contact"
        )
        assert contact.position is None
        assert contact.phone is None
        assert contact.email is None
        assert contact.is_principal is False
