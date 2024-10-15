import pytest
from accounts.models import CustomUserModel
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
class BaseViewTest:

    @pytest.fixture
    def client_logged(self, client):
        user = CustomUserModel.get('eduardouio7@gmail.com')
        client = Client()
        client.force_login(user)
        return client

    def test_anonymus_user(self, url):
        response = Client().get(url)
        response_url = reverse('login') + '?next=' + url
        assert response.status_code == 302
        assert response.url == response_url

    def test_loged_user(self, client_logged, url):
        response = client_logged.get(url)
        assert response.status_code == 200
