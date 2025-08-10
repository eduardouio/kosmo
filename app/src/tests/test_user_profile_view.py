import pytest
from django.urls import reverse
from django.utils import timezone
from django.test import Client

from accounts.models.CustomUserModel import CustomUserModel
from accounts.models.License import License


@pytest.mark.django_db
def test_profile_view_requires_login():
    client = Client()
    url = reverse('user_profile')
    resp = client.get(url)
    # Debe redirigir al login
    assert resp.status_code in (302, 301)
    assert 'accounts/login' in resp.url


@pytest.mark.django_db
def test_profile_view_ok_with_user_and_license():
    user = CustomUserModel.objects.create_user(
        email='user@example.com', password='secret123', first_name='U'
    )
    # Licencia más antigua inactiva
    License.objects.create(
        user=user,
        license_key='OLD-KEY-123',
        is_active=False,
        activated_on=timezone.now() - timezone.timedelta(days=10),
    )
    # Licencia activa más reciente
    License.objects.create(
        user=user,
        license_key='ACTIVE-KEY-456',
        is_active=True,
        activated_on=timezone.now(),
        enterprise='TESTCO',
    )

    client = Client()
    client.force_login(user)
    url = reverse('user_profile')
    resp = client.get(url)
    assert resp.status_code == 200
    # Renderiza el template esperado
    assert 'Perfil de Usuario' in resp.content.decode()
    # Contexto incluye el usuario
    assert resp.context['user_profile'].pk == user.pk
    # Muestra datos de la licencia activa
    body = resp.content.decode()
    assert 'ACTIVE-KEY-456' in body
    assert 'TESTCO' in body
