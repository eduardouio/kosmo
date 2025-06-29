import pytest
from datetime import date
from partners.models import DAE, Partner


@pytest.mark.django_db
class TestDAE:
    
    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )
        
    def test_create_dae(self, partner):
        """Test creación de DAE"""
        dae = DAE.objects.create(
            partner=partner,
            dae="dae123456789",
            awb="awb123456789",
            hawb="hawb123456789",
            cargo_agency="dhl express",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        assert dae.dae == "DAE123456789"
        assert dae.awb == "AWB123456789"
        assert dae.hawb == "HAWB123456789"
        assert dae.cargo_agency == "DHL EXPRESS"
        assert dae.date_begin == date(2024, 1, 1)
        assert dae.date_end == date(2024, 1, 31)
        
    def test_uppercase_conversion(self, partner):
        """Test conversión a mayúsculas en save"""
        dae = DAE.objects.create(
            partner=partner,
            dae="dae987654321",
            awb="awb987654321",
            hawb="hawb987654321",
            cargo_agency="fedex corporation",
            date_begin=date(2024, 2, 1),
            date_end=date(2024, 2, 28)
        )
        assert dae.dae == "DAE987654321"
        assert dae.awb == "AWB987654321"
        assert dae.hawb == "HAWB987654321"
        assert dae.cargo_agency == "FEDEX CORPORATION"
        
    def test_unique_dae_constraint(self, partner):
        """Test restricción unique del campo dae"""
        DAE.objects.create(
            partner=partner,
            dae="DAE123456789",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        
        # Crear otro partner para probar que el DAE debe ser único globalmente
        partner2 = Partner.objects.create(
            business_tax_id="0987654321",
            name="OTHER PARTNER",
            address="Av. Test 456",
            country="Ecuador",
            city="Guayaquil",
            type_partner="PROVEEDOR"
        )
        
        with pytest.raises(Exception):  # IntegrityError por unique constraint
            DAE.objects.create(
                partner=partner2,
                dae="DAE123456789",
                date_begin=date(2024, 2, 1),
                date_end=date(2024, 2, 28)
            )
            
    def test_get_last_by_partner(self, partner):
        """Test método classmethod get_last_by_partner"""
        # Crear varios DAE para el mismo partner
        dae1 = DAE.objects.create(
            partner=partner,
            dae="DAE001",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        dae2 = DAE.objects.create(
            partner=partner,
            dae="DAE002",
            date_begin=date(2024, 2, 1),
            date_end=date(2024, 2, 28)
        )
        dae3 = DAE.objects.create(
            partner=partner,
            dae="DAE003",
            date_begin=date(2024, 3, 1),
            date_end=date(2024, 3, 31)
        )
        
        last_dae = DAE.get_last_by_partner(partner)
        assert last_dae == dae3  # El último por fecha de fin
        
    def test_get_last_by_partner_none(self, partner):
        """Test get_last_by_partner cuando no hay DAE activos"""
        # Crear DAE inactivo
        dae = DAE.objects.create(
            partner=partner,
            dae="DAE001",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        dae.is_active = False
        dae.save()
        
        last_dae = DAE.get_last_by_partner(partner)
        assert last_dae is None
        
    def test_str_method(self, partner):
        """Test método __str__"""
        dae = DAE.objects.create(
            partner=partner,
            dae="DAE123456789",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        expected_str = "DAE123456789 TEST PARTNER"
        assert str(dae) == expected_str
        
    def test_optional_fields(self, partner):
        """Test campos opcionales"""
        dae = DAE.objects.create(
            partner=partner,
            dae="DAE123456789",
            date_begin=date(2024, 1, 1),
            date_end=date(2024, 1, 31)
        )
        assert dae.awb is None
        assert dae.hawb is None
        assert dae.cargo_agency is None
        
    def test_required_fields(self, partner):
        """Test campos requeridos"""
        # Test que partner, dae, date_begin y date_end son requeridos
        with pytest.raises(Exception):
            DAE.objects.create(
                dae="DAE123456789",
                date_begin=date(2024, 1, 1),
                date_end=date(2024, 1, 31)
            )
