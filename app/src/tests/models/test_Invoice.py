import pytest
from datetime import date
from decimal import Decimal
from trade.models import Invoice, Order
from partners.models import Partner
from products.models import StockDay


@pytest.mark.django_db
class TestInvoice:
    
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
        
    @pytest.fixture
    def order(self, partner, stock_day):
        """Fixture para crear una orden"""
        return Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CONFIRMADO"
        )
        
    def test_create_invoice(self, order, partner):
        """Test creación de factura"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            num_invoice="FAC-001",
            total_price=Decimal("1000.00"),
            total_margin=Decimal("100.00")
        )
        assert invoice.order == order
        assert invoice.partner == partner
        assert invoice.type_document == "FAC_VENTA"
        assert invoice.num_invoice == "FAC-001"
        assert invoice.total_price == Decimal("1000.00")
        assert invoice.total_margin == Decimal("100.00")
        
    def test_type_document_choices(self, order, partner):
        """Test choices de tipo de documento"""
        # Factura de venta
        invoice_sale = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA"
        )
        assert invoice_sale.type_document == "FAC_VENTA"
        
        # Factura de compra
        invoice_purchase = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_COMPRA"
        )
        assert invoice_purchase.type_document == "FAC_COMPRA"
        
    def test_status_choices(self, order, partner):
        """Test choices de status"""
        status_options = ['PENDIENTE', 'PAGADO', 'ANULADO']
        
        for status in status_options:
            invoice = Invoice.objects.create(
                order=order,
                partner=partner,
                type_document="FAC_VENTA",
                status=status
            )
            assert invoice.status == status
            
    def test_default_status(self, order, partner):
        """Test status por defecto"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA"
        )
        assert invoice.status == "PENDIENTE"
        
    def test_series_choices(self, order, partner):
        """Test choices de series"""
        # Serie 300
        invoice1 = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            serie="300"
        )
        assert invoice1.serie == "300"
        
        # Serie 000
        invoice2 = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            serie="000"
        )
        assert invoice2.serie == "000"
        
    def test_default_values(self, order, partner):
        """Test valores por defecto"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA"
        )
        assert invoice.total_price == 0
        assert invoice.total_margin == 0
        assert invoice.comision_seler == 0
        assert invoice.eb_total == 0
        assert invoice.qb_total == 0
        assert invoice.hb_total == 0
        assert invoice.fb_total == 0
        assert invoice.total_pieces == 0
        assert invoice.tot_stem_flower == 0
        assert invoice.total_bunches == 0
        assert invoice.num_invoice == ""
        
    def test_decimal_fields(self, order, partner):
        """Test campos decimales"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            total_price=Decimal("1250.75"),
            total_margin=Decimal("125.50"),
            comision_seler=Decimal("62.25"),
            fb_total=Decimal("10.5"),
            weight=Decimal("45.75")
        )
        assert invoice.total_price == Decimal("1250.75")
        assert invoice.total_margin == Decimal("125.50")
        assert invoice.comision_seler == Decimal("62.25")
        assert invoice.fb_total == Decimal("10.5")
        assert invoice.weight == Decimal("45.75")
        
    def test_integer_fields(self, order, partner):
        """Test campos enteros"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            consecutive=123,
            eb_total=50,
            qb_total=25,
            hb_total=30,
            total_pieces=105,
            tot_stem_flower=2625,
            total_bunches=105
        )
        assert invoice.consecutive == 123
        assert invoice.eb_total == 50
        assert invoice.qb_total == 25
        assert invoice.hb_total == 30
        assert invoice.total_pieces == 105
        assert invoice.tot_stem_flower == 2625
        assert invoice.total_bunches == 105
        
    def test_optional_fields(self, order, partner):
        """Test campos opcionales"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            marking="MARK-001",
            po_number="PO-001",
            awb="AWB123456",
            dae_export="DAE123456",
            hawb="HAWB123456",
            cargo_agency="DHL",
            delivery_date=date(2024, 1, 25)
        )
        assert invoice.marking == "MARK-001"
        assert invoice.po_number == "PO-001"
        assert invoice.awb == "AWB123456"
        assert invoice.dae_export == "DAE123456"
        assert invoice.hawb == "HAWB123456"
        assert invoice.cargo_agency == "DHL"
        assert invoice.delivery_date == date(2024, 1, 25)
        
    def test_auto_date_field(self, order, partner):
        """Test campo date con auto_now"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA"
        )
        assert invoice.date is not None
        # La fecha debería ser aproximadamente ahora
        from django.utils import timezone
        assert (timezone.now() - invoice.date).total_seconds() < 60
        
    def test_foreign_key_restrict(self, order, partner):
        """Test RESTRICT en foreign keys"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA"
        )
        
        # No se puede eliminar order si tiene facturas
        with pytest.raises(Exception):
            order.delete()
            
        # No se puede eliminar partner si tiene facturas
        with pytest.raises(Exception):
            partner.delete()
