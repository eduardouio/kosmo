import json
import pytest
from django.urls import reverse
from tests.BaseViewTest import BaseViewTest
from partners.models import Partner


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

    def test_post_kosmo(self, client_logged, url):
        partner = Partner.get_by_parcial_name("kosmo")
        post_data = {
            "id_partner": partner.id,
            "date": "2024-10-15",
            "stock_text": "Kosmo Flowers Availability- Oct 14th\n1hb Explorer 40/50 x 250 0,40/0,50"
        }
        response = client_logged.post(
            url, data=json.dumps(post_data), content_type='application/json'
        )
        assert response.status_code == 200


    def test_post_aroma(self, client_logged, url):
        partner = Partner.get_by_parcial_name("floraroma")
        post_data = {
            "id_partner": partner.id,
            "date": "2024-10-15",
            "stock_text": "AMARETO 1QB4050 $0.25-0.35"
        }
        response = client_logged.post(
            url, data=json.dumps(post_data), content_type='application/json'
        )
        assert response.status_code == 200