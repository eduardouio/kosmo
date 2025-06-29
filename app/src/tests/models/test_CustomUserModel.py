import pytest
from django.db import IntegrityError
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestCustomUserModel:

    def test_create_user(self):
        """Test creación de usuario"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123",
            first_name="Juan",
            last_name="Pérez"
        )
        assert user.email == "test@example.com"
        assert user.first_name == "Juan"
        assert user.last_name == "Pérez"
        assert user.roles == "ADMINISTRADOR"
        assert user.is_confirmed_mail is False
        assert user.check_password("testpass123")

    def test_unique_email_constraint(self):
        """Test restricción unique del email"""
        CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        with pytest.raises(IntegrityError):
            CustomUserModel.objects.create_user(
                email="test@example.com",
                password="testpass456"
            )

    def test_role_choices(self):
        """Test choices de roles"""
        # Administrador
        admin = CustomUserModel.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            roles="ADMINISTRADOR"
        )
        assert admin.roles == "ADMINISTRADOR"

        # Vendedor
        seller = CustomUserModel.objects.create_user(
            email="seller@example.com",
            password="testpass123",
            roles="VENDEDOR"
        )
        assert seller.roles == "VENDEDOR"

    def test_default_role(self):
        """Test rol por defecto"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        assert user.roles == "ADMINISTRADOR"

    def test_get_sellers(self):
        """Test método classmethod get_sellers"""
        admin = CustomUserModel.objects.create_user(
            email="admin@example.com",
            password="testpass123",
            roles="ADMINISTRADOR"
        )
        seller1 = CustomUserModel.objects.create_user(
            email="seller1@example.com",
            password="testpass123",
            roles="VENDEDOR"
        )
        seller2 = CustomUserModel.objects.create_user(
            email="seller2@example.com",
            password="testpass123",
            roles="VENDEDOR"
        )

        sellers = CustomUserModel.get_sellers()
        assert seller1 in sellers
        assert seller2 in sellers
        assert admin not in sellers
        assert sellers.count() == 2

    def test_get_method(self):
        """Test método classmethod get"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        found_user = CustomUserModel.get("test@example.com")
        assert found_user == user

        not_found = CustomUserModel.get("nonexistent@example.com")
        assert not_found is None

    def test_get_by_id(self):
        """Test método classmethod get_by_id"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

        found_user = CustomUserModel.get_by_id(user.id)
        assert found_user == user

        not_found = CustomUserModel.get_by_id(99999)
        assert not_found is None

    def test_str_method(self):
        """Test método __str__"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        assert str(user) == "test@example.com"

    def test_optional_fields(self):
        """Test campos opcionales"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123",
            phone="123456789",
            notes="Test notes",
            is_confirmed_mail=True
        )
        assert user.phone == "123456789"
        assert user.notes == "Test notes"
        assert user.is_confirmed_mail is True

    def test_username_field(self):
        """Test que email es el USERNAME_FIELD"""
        assert CustomUserModel.USERNAME_FIELD == "email"

    def test_required_fields(self):
        """Test REQUIRED_FIELDS"""
        assert CustomUserModel.REQUIRED_FIELDS == []

    def test_no_username(self):
        """Test que username es None"""
        user = CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
        assert user.username is None
