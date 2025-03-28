import pytest
from common import InvoiceOrder
from trade.models import Order, Invoice
from common.AppLoger import loggin_event


@pytest.mark.django_db
class TestCreateInvoiceOrder():
    def test_generate_not_aprve_order(self):
        loggin_event("[TEST] Pasando la prueba de orden no aprobada")
        order = Order.get_order_by_id(1)
        result = InvoiceOrder().generate_invoice(order)
        assert result is False

    def generate_supplier_invoice(self, order):
        loggin_event("[TEST] Pasando la prueba de orden compra aprobada")
        order = Order.get_order_by_id(9)
        result = InvoiceOrder().generate_invoice(order)
        assert isinstance(result, Invoice)
