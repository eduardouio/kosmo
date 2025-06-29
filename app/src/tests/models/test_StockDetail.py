import pytest
from datetime import date
from products.models import StockDetail, StockDay, BoxItems
from partners.models import Partner


@pytest.mark.django_db
class TestStockDetail:

    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un stock day"""
        return StockDay.objects.create(date=date(2024, 1, 15))

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

    def test_create_stock_detail(self, stock_day, partner):
        """Test creación de stock detail"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            quantity=10,
            box_model="HB",
            tot_stem_flower=250,
            tot_cost_price_box=5.50,
            profit_margin=0.08
        )
        assert stock_detail.stock_day == stock_day
        assert stock_detail.partner == partner
        assert stock_detail.quantity == 10
        assert stock_detail.box_model == "HB"
        assert stock_detail.tot_stem_flower == 250
        assert stock_detail.tot_cost_price_box == 5.50
        assert stock_detail.profit_margin == 0.08

    def test_box_model_choices(self, stock_day, partner):
        """Test choices de box_model"""
        box_models = ['HB', 'QB', 'FB', 'EB']

        for box_model in box_models:
            stock_detail = StockDetail.objects.create(
                stock_day=stock_day,
                partner=partner,
                quantity=1,
                box_model=box_model
            )
            assert stock_detail.box_model == box_model

    def test_default_values(self, stock_day, partner):
        """Test valores por defecto"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )
        assert stock_detail.quantity == 0
        assert stock_detail.tot_stem_flower == 0
        assert stock_detail.tot_cost_price_box == 0.00
        assert stock_detail.profit_margin == 0.06

    def test_get_by_stock_day(self, stock_day, partner):
        """Test método classmethod get_by_stock_day"""
        stock_detail1 = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )
        stock_detail2 = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="QB"
        )

        # Crear stock detail inactivo (no debería aparecer)
        inactive_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="EB"
        )
        inactive_detail.is_active = False
        inactive_detail.save()

        stock_details = StockDetail.get_by_stock_day(stock_day)
        assert stock_detail1 in stock_details
        assert stock_detail2 in stock_details
        assert inactive_detail not in stock_details
        assert stock_details.count() == 2

    def test_get_partner_by_stock_day(self, stock_day):
        """Test método classmethod get_partner_by_stock_day"""
        partner1 = Partner.objects.create(
            business_tax_id="1234567890",
            name="PARTNER 1",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )
        partner2 = Partner.objects.create(
            business_tax_id="0987654321",
            name="PARTNER 2",
            address="Av. Test 456",
            country="Ecuador",
            city="Guayaquil",
            type_partner="PROVEEDOR"
        )

        StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner1,
            box_model="HB"
        )
        StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner2,
            box_model="QB"
        )

        partners = StockDetail.get_partner_by_stock_day(stock_day)
        assert partner1 in partners
        assert partner2 in partners
        assert len(partners) == 2

    def test_get_stock_day_partner(self, stock_day, partner):
        """Test método classmethod get_stock_day_partner"""
        stock_detail1 = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )
        stock_detail2 = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="QB"
        )

        stock_details = StockDetail.get_stock_day_partner(stock_day, partner)
        assert stock_detail1 in stock_details
        assert stock_detail2 in stock_details
        assert stock_details.count() == 2

    def test_disable_stock_detail(self, stock_day, partner):
        """Test método classmethod disable_stock_detail"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )

        StockDetail.disable_stock_detail(stock_day, partner)
        stock_detail.refresh_from_db()
        assert stock_detail.is_active is False

    def test_get_by_id(self, stock_day, partner):
        """Test método classmethod get_by_id"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )

        found_detail = StockDetail.get_by_id(stock_detail.id)
        assert found_detail == stock_detail

        not_found = StockDetail.get_by_id(99999)
        assert not_found is None

    def test_str_method(self, stock_day, partner):
        """Test método __str__"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )
        assert str(stock_detail) == str(stock_day)

    def test_foreign_key_cascade(self, stock_day, partner):
        """Test cascade al eliminar stock_day o partner"""
        stock_detail = StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )

        stock_detail_id = stock_detail.id

        # Eliminar stock_day debería eliminar stock_detail por CASCADE
        StockDay.objects.filter(id=stock_day.id).delete()

        with pytest.raises(StockDetail.DoesNotExist):
            StockDetail.objects.get(id=stock_detail_id)
