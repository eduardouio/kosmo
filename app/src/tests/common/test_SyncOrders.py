# Para correr los test cargte la informacion de teste desde el sowsed.py
import pytest
from trade.models import Order, OrderBoxItems, OrderItems
from common import SyncOrders
from django.urls import reverse
from django.test import Client
from accounts.models import CustomUserModel
from common.AppLoger import loggin_event


@pytest.mark.django_db
class TestSyncOrdersCustomers:

    @pytest.fixture
    def client_logged(self, client):
        user = CustomUserModel.get('eduardouio7@gmail.com')
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def url_uptd_customer(self):
        return reverse('update_order')

    @pytest.fixture
    def url_updt_supplier(self):
        return reverse('update_supplier_order')

    def test_update_cus_order_add_quantity(self):
        loggin_event(
            'Test de Modify Customer Order, afecta ordernes de compra'
        )
        loggin_event('Modificamos la ordern de compra #1')
        old_order_item = OrderItems.get_by_id(1)
        order_item = OrderItems.get_by_id(1)
        order_item.quantity = 1
        order_item.save()
        OrderItems.rebuild_order_item(order_item)
        Order.rebuild_totals(order_item.order)
        assert old_order_item.quantity != order_item.quantity
        assert old_order_item.order.qb_total == order_item.order.qb_total
        assert order_item.order.total_price == 4322.50
        assert order_item.order.qb_total == 58
        assert order_item.order.total_stem_flower == 7250

        # actualizar orden de compra
        loggin_event('Actualizamos la orden de compra')
        SyncOrders.update_order(order_item.order)
        loggin_event('Verificamos que la orden de compra se actualizo')