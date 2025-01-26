import pytest
from django.urls import reverse
from django.test import Client

from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestStockDetailAPI():

    @pytest.fixture
    def client(self):
        client = Client()
        client.force_login(CustomUserModel.get('eduardouio7@gmail.com'))
        return Client()

    @ pytest.fixture
    def url(self):
        return reverse('stock_detail', args=[1])

    def test_get_stock_dont_exist(self, client):
        response = client.get('/api/stock_detail/20/')
        assert response.status_code == 404
        assert response.json()['error'] == 'No hay detalles para esta diponibilidad, debe importar primero'

    def test_get_stock_exist(self, client, url):
        response = client.get(url)
        spected_data = {
            'sotck': [],
            'sotckDay': {
                'id': 1,
            },
            'orders': []
        }

        response_data = response.json()
        assert 'stock' in response_data.keys()
        assert 'stockDay' in response_data.keys()
        assert 'orders' in response_data.keys()
        assert response_data['stockDay']['id'] == spected_data['sotckDay']['id']
        assert response.status_code == 200
