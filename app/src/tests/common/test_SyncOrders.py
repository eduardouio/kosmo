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

    def test_update_cus_order(self):
        loggin_event(
            'Test de Modify Customer Order, afecta ordernes de compra'
        )
        loggin_event('Modificamos la ordern de compra #1')
        order = Order.objects.get(pk=1)
        order_items = OrderItems.get_by_order(order)

        for ord_item in order_items:
            box_items = OrderBoxItems.get_by_order_item(ord_item)
            for box_item in box_items:
                box_item.delete()
            ord_item.delete()
        