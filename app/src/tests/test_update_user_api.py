import pytest
from django.urls import reverse
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models.CustomUserModel import CustomUserModel


@pytest.mark.django_db
def test_update_profile_basic_fields():
    user = CustomUserModel.objects.create_user(
        email='user@example.com', password='secret123', first_name='Old'
    )
    client = Client()
    client.force_login(user)

    url = reverse('update_user')
    payload = {
        'first_name': 'NewName',
        'last_name': 'NewLast',
        'phone': '0999999999',
        'notes': 'nota',
        'email': 'user@example.com',
    }
    resp = client.post(url, data=payload)
    assert resp.status_code == 200

    user.refresh_from_db()
    assert user.first_name == 'NewName'
    assert user.last_name == 'NewLast'
    assert user.phone == '0999999999'
    assert user.notes == 'nota'


@pytest.mark.django_db
def test_update_profile_picture():
    user = CustomUserModel.objects.create_user(
        email='user2@example.com', password='secret123'
    )
    client = Client()
    client.force_login(user)

    url = reverse('update_user')
    image_content = (
        b"\x47\x49\x46\x38\x39\x61\x02\x00\x01\x00\x80\x00\x00"
        b"\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\n\x00\x01\x00,\x00"
        b"\x00\x00\x00\x02\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )
    file = SimpleUploadedFile(
        'tiny.gif', image_content, content_type='image/gif'
    )

    resp = client.post(url, data={'picture': file})
    assert resp.status_code == 200
    user.refresh_from_db()
    assert bool(user.picture)


@pytest.mark.django_db
def test_change_password_flow():
    user = CustomUserModel.objects.create_user(
        email='user3@example.com', password='oldpass123'
    )
    client = Client()
    client.force_login(user)

    url = reverse('update_user')
    resp = client.post(
        url,
        data={
            'action': 'change_password',
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123',
        },
        content_type='application/json',
    )
    assert resp.status_code == 200

    # Ahora el usuario debe poder autenticarse con la nueva contraseña
    client.logout()
    assert client.login(
        email='user3@example.com', password='newpass123'
    ) is True
