import pytest
from datetime import date
from partners.models import Partner


@pytest.mark.django_db
class TestPartner:
    
    def test_create_partner(self):
        """Test creación de partner"""
        partner = Partner.objects.create(
            business_tax_id="1234567890",
            name="KOSMO FLOWERS",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )
        assert partner.name == "KOSMO FLOWERS"
        assert partner.status == "APROBADO"
        assert partner.default_profit_margin == 0.00
        assert partner.credit_term == 0
        assert partner.is_profit_margin_included is False
        assert partner.consolidate is False
        assert partner.is_verified is False
        
    def test_partner_type_choices(self):
        """Test choices de tipo de partner"""
        # Cliente
        client = Partner.objects.create(
            business_tax_id="1234567891",
            name="CLIENT TEST",
            address="Av. Test 123",
            country="Ecuador", 
            city="Quito",
            type_partner="CLIENTE"
        )
        assert client.type_partner == "CLIENTE"
        
        # Proveedor
        supplier = Partner.objects.create(
            business_tax_id="1234567892",
            name="SUPPLIER TEST",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito", 
            type_partner="PROVEEDOR"
        )
        assert supplier.type_partner == "PROVEEDOR"
        
    def test_status_choices(self):
        """Test choices de status"""
        partner = Partner.objects.create(
            business_tax_id="1234567893",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            status="PENDIENTE"
        )
        assert partner.status == "PENDIENTE"
        
    def test_many_to_many_partner(self):
        """Test relación many to many con partners"""
        supplier = Partner.objects.create(
            business_tax_id="1234567894",
            name="SUPPLIER TEST",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )
        
        client = Partner.objects.create(
            business_tax_id="1234567895",
            name="CLIENT TEST",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )
        
        client.partner.add(supplier)
        assert supplier in client.partner.all()
        
    def test_optional_fields(self):
        """Test campos opcionales"""
        partner = Partner.objects.create(
            business_tax_id="1234567896",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            short_name="TEST",
            email="test@test.com",
            phone="123456789",
            website="www.test.com",
            dispatch_days=5,
            seller="Juan Pérez"
        )
        assert partner.short_name == "TEST"
        assert partner.email == "test@test.com"
        assert partner.phone == "123456789"
        assert partner.website == "www.test.com"  # Se convierte a mayúsculas
        assert partner.dispatch_days == 5
        assert partner.seller == "JUAN PÉREZ"
        
    def test_date_fields(self):
        """Test campos de fecha"""
        test_date = date(2024, 1, 1)
        partner = Partner.objects.create(
            business_tax_id="1234567897",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            date_aproved=test_date,
            businnes_start=test_date
        )
        assert partner.date_aproved == test_date
        assert partner.businnes_start == test_date
        
    def test_decimal_fields(self):
        """Test campos decimales"""
        partner = Partner.objects.create(
            business_tax_id="1234567898",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            default_profit_margin=0.15
        )
        assert partner.default_profit_margin == 0.15
        
    def test_boolean_fields(self):
        """Test campos booleanos"""
        partner = Partner.objects.create(
            business_tax_id="1234567899",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            is_profit_margin_included=True,
            consolidate=True,
            is_verified=True
        )
        assert partner.is_profit_margin_included is True
        assert partner.consolidate is True
        assert partner.is_verified is True
