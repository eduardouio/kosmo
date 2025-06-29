import pytest
from datetime import date
from decimal import Decimal
from trade.models import Order
from partners.models import Partner
from products.models import StockDay


@pytest.mark.django_db
class TestOrder:
    
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
        
    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un stock day"""
        return StockDay.objects.create(date=date(2024, 1, 15))
        
    def test_create_order(self, partner, stock_day):
        """Test creación de orden"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            delivery_date=date(2024, 1, 20),
            num_order="PO-001"
        )
        assert order.partner == partner
        assert order.stock_day == stock_day
        assert order.type_document == "ORD_VENTA"
        assert order.status == "PENDIENTE"
        assert order.delivery_date == date(2024, 1, 20)
        assert order.num_order == "PO-001"
        
    def test_type_document_choices(self, partner, stock_day):
        """Test choices de tipo de documento"""
        # Orden de venta
        order_sale = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE"
        )
        assert order_sale.type_document == "ORD_VENTA"
        
        # Orden de compra
        order_purchase = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_COMPRA",
            status="PENDIENTE"
        )
        assert order_purchase.type_document == "ORD_COMPRA"
        
    def test_status_choices(self, partner, stock_day):
        """Test choices de status"""
        status_options = ['PENDIENTE', 'CONFIRMADO', 'MODIFICADO', 
                         'FACTURADO', 'CANCELADO', 'PROMESA']
        
        for status in status_options:
            order = Order.objects.create(
                partner=partner,
                stock_day=stock_day,
                type_document="ORD_VENTA",
                status=status
            )
            assert order.status == status
            
    def test_default_values(self, partner, stock_day):
        """Test valores por defecto"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE"
        )
        assert order.discount == 0
        assert order.total_price == 0
        assert order.total_margin == 0
        assert order.total_bunches == 0
        assert order.comision_seler == 0
        assert order.eb_total == 0
        assert order.qb_total == 0
        assert order.hb_total == 0
        assert order.fb_total == 0
        assert order.total_stem_flower == 0
        assert order.is_invoiced is False
        assert order.id_invoice == 0
        
    def test_series_choices(self, partner, stock_day):
        """Test choices de series"""
        # Serie 100
        order1 = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            serie="100"
        )
        assert order1.serie == "100"
        
        # Serie 200
        order2 = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            serie="200"
        )
        assert order2.serie == "200"
        
    def test_parent_order_self_reference(self, partner, stock_day):
        """Test relación parent_order (self reference)"""
        parent_order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CONFIRMADO"
        )
        
        child_order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="MODIFICADO",
            parent_order=parent_order
        )
        
        assert child_order.parent_order == parent_order
        
    def test_decimal_fields(self, partner, stock_day):
        """Test campos decimales"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            discount=Decimal("50.25"),
            total_price=Decimal("1250.75"),
            total_margin=Decimal("125.50"),
            comision_seler=Decimal("62.50"),
            fb_total=Decimal("10.5")
        )
        assert order.discount == Decimal("50.25")
        assert order.total_price == Decimal("1250.75")
        assert order.total_margin == Decimal("125.50")
        assert order.comision_seler == Decimal("62.50")
        assert order.fb_total == Decimal("10.5")
        
    def test_optional_fields(self, partner, stock_day):
        """Test campos opcionales"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE"
        )
        assert order.serie is None
        assert order.consecutive is None
        assert order.delivery_date is None
        assert order.num_order is None
        assert order.num_invoice is None
        
    def test_foreign_key_restrict(self, partner, stock_day):
        """Test RESTRICT en foreign keys"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE"
        )
        
        # No se puede eliminar partner si tiene órdenes
        with pytest.raises(Exception):
            partner.delete()
            
        # No se puede eliminar stock_day si tiene órdenes
        with pytest.raises(Exception):
            stock_day.delete()
            
    def test_auto_date_field(self, partner, stock_day):
        """Test campo date con auto_now"""
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE"
        )
        assert order.date is not None
        # La fecha debería ser aproximadamente ahora
        from django.utils import timezone
        assert (timezone.now() - order.date).total_seconds() < 60
