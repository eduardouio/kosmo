import pytest
from datetime import datetime
from django.db import IntegrityError
from accounts.models import License, CustomUserModel


@pytest.mark.django_db
class TestLicense:

    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    def test_create_license(self, user):
        """Test creación de licencia"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY-123",
            user=user,
            enterprise="KOSMOFLOWERS",
            is_active=True,
            url_server="https://test.kosmoflowers.com"
        )
        assert license_obj.license_key == "TEST-LICENSE-KEY-123"
        assert license_obj.user == user
        assert license_obj.enterprise == "KOSMOFLOWERS"
        assert license_obj.is_active is True
        assert license_obj.url_server == "https://test.kosmoflowers.com"

    def test_unique_license_key_constraint(self, user):
        """Test restricción unique del license_key"""
        License.objects.create(
            license_key="UNIQUE-LICENSE-KEY",
            user=user
        )

        user2 = CustomUserModel.objects.create_user(
            email="test2@example.com",
            password="testpass123"
        )

        with pytest.raises(IntegrityError):
            License.objects.create(
                license_key="UNIQUE-LICENSE-KEY",
                user=user2
            )

    def test_default_values(self, user):
        """Test valores por defecto"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user
        )
        assert license_obj.enterprise == "KOSMOFLOWERS"
        assert license_obj.is_active is False
        assert license_obj.activated_on is None
        assert license_obj.expires_on is None
        assert license_obj.url_server is None

    def test_date_fields(self, user):
        """Test campos de fecha"""
        activated_date = datetime(2024, 1, 1, 12, 0, 0)
        expires_date = datetime(2024, 12, 31, 23, 59, 59)

        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user,
            activated_on=activated_date,
            expires_on=expires_date
        )
        assert license_obj.activated_on == activated_date
        assert license_obj.expires_on == expires_date

    def test_str_method(self, user):
        """Test método __str__"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user
        )
        expected_str = f"Licencia de {user.email}"
        assert str(license_obj) == expected_str

    def test_foreign_key_cascade(self, user):
        """Test cascade al eliminar usuario"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user
        )

        user_id = user.id
        license_id = license_obj.id

        # Eliminar usuario debería eliminar la licencia por CASCADE
        user.delete()

        with pytest.raises(License.DoesNotExist):
            License.objects.get(id=license_id)

    def test_optional_fields_null(self, user):
        """Test que campos opcionales pueden ser null"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user,
            activated_on=None,
            expires_on=None,
            url_server=None
        )
        assert license_obj.activated_on is None
        assert license_obj.expires_on is None
        assert license_obj.url_server is None

    def test_enterprise_custom_value(self, user):
        """Test valor personalizado de enterprise"""
        license_obj = License.objects.create(
            license_key="TEST-LICENSE-KEY",
            user=user,
            enterprise="CUSTOM ENTERPRISE"
        )
        assert license_obj.enterprise == "CUSTOM ENTERPRISE"

    def test_boolean_field(self, user):
        """Test campo booleano is_active"""
        # Test True
        license_active = License.objects.create(
            license_key="ACTIVE-LICENSE",
            user=user,
            is_active=True
        )
        assert license_active.is_active is True

        # Test False (default)
        user2 = CustomUserModel.objects.create_user(
            email="test2@example.com",
            password="testpass123"
        )
        license_inactive = License.objects.create(
            license_key="INACTIVE-LICENSE",
            user=user2,
            is_active=False
        )
        assert license_inactive.is_active is False
