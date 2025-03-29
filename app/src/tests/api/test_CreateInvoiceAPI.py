import json
import pytest
from django.urls import reverse
from django.test import Client
from common.AppLoger import loggin_event
from trade.models import Order

from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestCreateInvoiceAPI:

    @pytest.fixture
    def url(self):
        return reverse('create_invoice_by_order')

    @pytest.fixture
    def client_logged(self):
        user = CustomUserModel.get("eduardouio7@gmail.com")
        client = Client()
        client.force_login(user)
        return client

    def test_create_invoice_success(self, client_logged, url):
        loggin_event('[TEST] Test para orden pendiente')
        order = Order.get_order_by_id(1)
        order.status = 'PENDIENTE'
        order.save()
        response = client_logged.post(
            url,
            data=json.dumps({'order_id': 1}),
            content_type='application/json'
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Pedido Pendiente'}

    def test_succes_created(self, client_logged, url):
        loggin_event(
            '[TEST] Test para orden confirmada se deben facturar las de compra'
        )
        response = client_logged.post(
            url,
            data=json.dumps({'order_id': 8}),
            content_type='application/json'
        )
        assert response.status_code == 201


        
