import pytest
from partners.models import Bank, Partner


@pytest.mark.django_db
class TestBank:
    
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
        
    def test_create_bank(self, partner):
        """Test creación de banco"""
        bank = Bank.objects.create(
            partner=partner,
            owner="juan perez",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="banco pichincha",
            swift_code="bpicecegxxx",
            iban="ec123456789",
            national_bank=True
        )
        assert bank.owner == "JUAN PEREZ"
        assert bank.id_owner == "1234567890"
        assert bank.account_number == "123456789"
        assert bank.bank_name == "BANCO PICHINCHA"
        assert bank.swift_code == "BPICECEGXXX"
        assert bank.iban == "EC123456789"
        assert bank.national_bank is True
        
    def test_uppercase_conversion(self, partner):
        """Test conversión a mayúsculas en save"""
        bank = Bank.objects.create(
            partner=partner,
            owner="maría gonzález",
            id_owner="0987654321",
            account_number="987654321",
            bank_name="banco del pacífico",
            swift_code="bpacecegxxx",
            iban="ec987654321"
        )
        assert bank.owner == "MARÍA GONZÁLEZ"
        assert bank.id_owner == "0987654321"
        assert bank.account_number == "987654321"
        assert bank.bank_name == "BANCO DEL PACÍFICO"
        assert bank.swift_code == "BPACECEGXXX"
        assert bank.iban == "EC987654321"
        
    def test_national_bank_default(self, partner):
        """Test valor por defecto de national_bank"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="Test Bank"
        )
        assert bank.national_bank is True
        
    def test_international_bank(self, partner):
        """Test banco internacional"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="Wells Fargo",
            national_bank=False
        )
        assert bank.national_bank is False
        
    def test_get_by_partner(self, partner):
        """Test método classmethod get_by_partner"""
        bank1 = Bank.objects.create(
            partner=partner,
            owner="Owner 1",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="Bank 1"
        )
        bank2 = Bank.objects.create(
            partner=partner,
            owner="Owner 2",
            id_owner="0987654321",
            account_number="987654321",
            bank_name="Bank 2"
        )
        
        banks = Bank.get_by_partner(partner)
        assert bank1 in banks
        assert bank2 in banks
        assert banks.count() == 2
        
    def test_str_method_national(self, partner):
        """Test método __str__ para banco nacional"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="banco pichincha",
            national_bank=True
        )
        assert str(bank) == "Nac: BANCO PICHINCHA"
        
    def test_str_method_international(self, partner):
        """Test método __str__ para banco internacional"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="wells fargo",
            national_bank=False
        )
        assert str(bank) == "Ext: WELLS FARGO"
        
    def test_optional_fields(self, partner):
        """Test campos opcionales"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="Test Bank"
        )
        assert bank.swift_code is None
        assert bank.iban is None
        
    def test_related_name(self, partner):
        """Test related_name 'banks'"""
        bank = Bank.objects.create(
            partner=partner,
            owner="Test Owner",
            id_owner="1234567890",
            account_number="123456789",
            bank_name="Test Bank"
        )
        assert bank in partner.banks.all()
