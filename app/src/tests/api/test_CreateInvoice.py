import pytest
from common import CreateInvoiceByOrder
from trade.models import Order, Invoice
from common.AppLoger import loggin_event


@pytest.mark.django_db
class TestCreateInvoiceOrder():
    def test_generate_not_aprve_order(self):
        loggin_event("[TEST] Pasando la prueba de orden no aprobada")
        order = Order.get_order_by_id(1)
        result = CreateInvoiceByOrder().generate_invoice(order)
        assert result is False

    def test_generate_supplier_invoice(self):
        loggin_event("[TEST] Pasando la prueba de orden compra aprobada")
        order = Order.get_order_by_id(9)
        Order.rebuild_totals(order)
        result = CreateInvoiceByOrder().generate_invoice(order)
        assert isinstance(result, Invoice)
        assert result.partner == order.partner
        assert result.type_document == 'FAC_COMPRA'
        assert result.total_price == order.total_price
        assert result.status == 'PENDIENTE'
        assert result.order == order
        assert result.qb_total == 3
        assert result.hb_total == 2
        assert result.total_price == 508.75
        assert result.total_margin == 63.75
        assert result.tot_stem_flower == 1275

    def test_generate_invoice_customer(self):
        loggin_event("[TEST] Pasando la prueba de orden venta aprobada")
        order = Order.get_order_by_id(8)
        Order.rebuild_totals(order)
        result = CreateInvoiceByOrder().generate_invoice(order)
        assert isinstance(result, Invoice)
        assert result.partner == order.partner
        assert result.type_document == 'FAC_VENTA'
        assert result.status == 'PENDIENTE'
        assert result.order == order
        assert result.qb_total == 13
        assert result.hb_total == 3
        assert result.total_price == 1514.50
        assert result.total_margin == 195.75
        assert result.tot_stem_flower == 2925
        assert result.total_price == order.total_price
        assert order.status == 'FACTURADO'
        parent_ordes = Order.get_by_parent_order(order)
        assert len(parent_ordes) == 2
        for supp_order in parent_ordes:
            assert supp_order.status == 'FACTURADO'
            assert supp_order.id_invoice > 0

