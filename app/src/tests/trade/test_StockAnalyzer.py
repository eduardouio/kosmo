import pytest
from django.urls import reverse
from tests.BaseViewTest import BaseViewTest


@pytest.mark.django_db
class TestStockDiary(BaseViewTest):

    @pytest.fixture
    def url(self):
        url = reverse('stock-add')
        return url

    def test_get_contex_tada(self, client_logged, url):
        response = client_logged.get(url)
        speceted_data_keys = [
            'view', 'title_page', 'products_json',
            'partners_json', 'products', 'partners'
        ]
        assert speceted_data_keys == list(response.context_data.keys())
        assert 'forms/stock-form.html' in response.template_name
        assert response.context_data['title_page'] == 'Disponibilidad'
