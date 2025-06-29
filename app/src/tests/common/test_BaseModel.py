import pytest
from accounts.models import CustomUserModel
from products.models import Product  # Un modelo que hereda de BaseModel
from common import BaseModel
from crum import impersonate


@pytest.mark.django_db
class TestBaseModel:

    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @pytest.fixture
    def product(self):
        """Fixture para crear un producto (hereda de BaseModel)"""
        return Product.objects.create(
            name="TEST PRODUCT",
            variety="TEST VARIETY"
        )

    def test_base_model_fields_exist(self, product):
        """Test que BaseModel tiene los campos esperados"""
        assert hasattr(product, 'notes')
        assert hasattr(product, 'created_at')
        assert hasattr(product, 'updated_at')
        assert hasattr(product, 'is_active')
        assert hasattr(product, 'id_user_created')
        assert hasattr(product, 'id_user_updated')
        assert hasattr(product, 'history')

    def test_default_values(self, product):
        """Test valores por defecto de BaseModel"""
        assert product.notes is None
        assert product.is_active is True
        assert product.id_user_created == 0
        assert product.id_user_updated == 0
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_save_with_user(self, user):
        """Test guardar con usuario actual"""
        with impersonate(user):
            product = Product.objects.create(
                name="TEST WITH USER",
                variety="TEST VARIETY"
            )

            assert product.id_user_created == user.pk
            assert product.id_user_updated == user.pk

    def test_save_without_user(self):
        """Test guardar sin usuario"""
        # Sin usuario actual
        with impersonate(None):
            product = Product.objects.create(
                name="TEST WITHOUT USER",
                variety="TEST VARIETY"
            )

            assert product.id_user_created == 0
            assert product.id_user_updated == 0

    def test_update_with_user(self, user, product):
        """Test actualizar con usuario"""
        original_created = product.id_user_created

        with impersonate(user):
            product.name = "UPDATED NAME"
            product.save()

            # El creador no debe cambiar, pero el actualizador sí
            assert product.id_user_created == original_created
            assert product.id_user_updated == user.pk

    def test_user_creator_property(self, user):
        """Test propiedad user_creator"""
        with impersonate(user):
            product = Product.objects.create(
                name="TEST CREATOR",
                variety="TEST VARIETY"
            )

            creator = product.user_creator
            assert creator is not None
            assert creator.email == user.email

    def test_user_creator_property_no_user(self, product):
        """Test propiedad user_creator sin usuario"""
        # Producto creado sin usuario
        creator = product.user_creator
        assert creator is None

    def test_get_create_user_method(self, user):
        """Test método get_create_user"""
        with impersonate(user):
            product = Product.objects.create(
                name="TEST GET CREATE USER",
                variety="TEST VARIETY"
            )

            creator = product.get_create_user()
            assert creator is not None
            assert creator.email == user.email

    def test_get_create_user_method_no_user(self, product):
        """Test método get_create_user sin usuario"""
        creator = product.get_create_user()
        assert creator is None

    def test_get_update_user_method(self, user, product):
        """Test método get_update_user"""
        with impersonate(user):
            product.name = "UPDATED"
            product.save()

            updater = product.get_update_user()
            assert updater is not None
            assert updater.email == user.email

    def test_get_by_id_classmethod(self, product):
        """Test método classmethod get_by_id"""
        found_product = Product.get_by_id(product.id)
        assert found_product == product

    def test_get_by_id_inactive(self, product):
        """Test get_by_id con registro inactivo"""
        product.is_active = False
        product.save()

        with pytest.raises(
            Exception, match="El registro no existe o fue eliminado"
        ):
            Product.get_by_id(product.id)

    def test_get_by_id_not_found(self):
        """Test get_by_id con id inexistente"""
        result = Product.get_by_id(99999)
        assert result is None

    def test_get_all_classmethod(self):
        """Test método classmethod get_all"""
        # Crear productos activos e inactivos
        active1 = Product.objects.create(name="ACTIVE 1", variety="VAR1")
        active2 = Product.objects.create(name="ACTIVE 2", variety="VAR2")
        inactive = Product.objects.create(name="INACTIVE", variety="VAR3")
        inactive.is_active = False
        inactive.save()

        all_products = Product.get_all()

        assert active1 in all_products
        assert active2 in all_products
        assert inactive not in all_products

    def test_get_all_inactive_classmethod(self):
        """Test método classmethod get_all_inactive"""
        active = Product.objects.create(name="ACTIVE", variety="VAR1")
        inactive = Product.objects.create(name="INACTIVE", variety="VAR2")
        inactive.is_active = False
        inactive.save()

        inactive_products = Product.get_all_inactive()

        assert active not in inactive_products
        assert inactive in inactive_products

    def test_get_all_with_inactive_classmethod(self):
        """Test método classmethod get_all_with_inactive"""
        active = Product.objects.create(name="ACTIVE", variety="VAR1")
        inactive = Product.objects.create(name="INACTIVE", variety="VAR2")
        inactive.is_active = False
        inactive.save()

        all_products = Product.get_all_with_inactive()

        assert active in all_products
        assert inactive in all_products

    def test_delete_method(self, product):
        """Test método delete (soft delete)"""
        product_id = product.id

        result = product.delete(product_id)

        assert result is True

        # Verificar que el producto aún existe pero está inactivo
        updated_product = Product.objects.get(id=product_id)
        assert updated_product.is_active is False

    def test_get_all_related_method(self, product):
        """Test método get_all_related"""
        # Crear otro producto
        Product.objects.create(name="ANOTHER", variety="VAR")

        related = product.get_all_related()
        assert len(related) >= 2  # Al menos 2 productos activos

    def test_get_all_related_with_inactive_method(self, product):
        """Test método get_all_related_with_inactive"""
        # Crear producto inactivo
        inactive = Product.objects.create(name="INACTIVE", variety="VAR")
        inactive.is_active = False
        inactive.save()

        all_related = product.get_all_related_with_inactive()
        assert inactive in all_related

    def test_history_tracking(self, product):
        """Test que el historial se registra correctamente"""
        # Modificar el producto
        product.name = "MODIFIED NAME"
        product.save()

        # Verificar que hay registros históricos
        history = product.history.all()
        assert len(history) >= 2  # Al menos creación y modificación

        # Verificar que el último registro tiene el nombre modificado
        latest_history = history.first()
        assert latest_history.name == "MODIFIED NAME"

    def test_meta_options(self):
        """Test opciones de Meta"""
        meta = BaseModel._meta
        assert meta.abstract is True
        assert meta.get_latest_by == 'created_at'

    def test_timestamps_auto_update(self, product):
        """Test que las fechas se actualizan automáticamente"""
        original_created = product.created_at
        original_updated = product.updated_at

        # Esperar un poco y actualizar
        import time
        time.sleep(0.1)

        product.name = "UPDATED"
        product.save()

        # created_at no debe cambiar, updated_at sí
        assert product.created_at == original_created
        assert product.updated_at > original_updated
