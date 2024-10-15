import pytest
import json
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
        assert response.status_code == 200
        