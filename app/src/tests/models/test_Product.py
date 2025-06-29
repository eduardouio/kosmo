import pytest
from django.db import IntegrityError
from products.models import Product


@pytest.mark.django_db
class TestProduct:
    
    def test_create_product(self):
        """Test creación de producto"""
        product = Product.objects.create(
            name="Rosa",
            variety="Explorer1",
            colors="RED,PINK"
        )
        assert product.name == "ROSA"
        assert product.variety == "EXPLORER1"
        assert product.colors == "RED,PINK"
        assert product.default_profit_margin == 0.06
        
    def test_uppercase_conversion(self):
        """Test conversión a mayúsculas en save"""
        product = Product.objects.create(
            name="rosa",
            variety="explorer2",
            colors="red,pink"
        )
        assert product.name == "ROSA"
        assert product.variety == "EXPLORER2"
        assert product.colors == "RED,PINK"
        
    def test_unique_together_constraint(self):
        """Test restricción unique_together de name y variety"""
        Product.objects.create(
            name="Clavel",
            variety="Standard"
        )
        with pytest.raises(IntegrityError):
            Product.objects.create(
                name="Clavel",
                variety="Standard"
            )
            
    def test_get_by_variety(self):
        """Test método classmethod get_by_variety"""
        product = Product.objects.create(
            name="Girasol",
            variety="Premium Test Unique"  # Usar variedad única
        )
        found = Product.get_by_variety("Premium Test Unique")
        assert found.id == product.id  # Comparar por ID en lugar del objeto
        assert found.variety == "PREMIUM TEST UNIQUE"
        
        # Test case insensitive
        found = Product.get_by_variety("premium test unique")
        assert found.id == product.id
        
        # Test not found
        not_found = Product.get_by_variety("NonExistent")
        assert not_found is None
        
    def test_str_method(self):
        """Test método __str__"""
        product = Product.objects.create(
            name="Tulipan",
            variety="Holandés"
        )
        assert str(product) == "TULIPAN - HOLANDÉS"
        
    def test_default_values(self):
        """Test valores por defecto"""
        product = Product.objects.create(
            name="Orquídea",
            variety="Tropical"
        )
        assert product.colors == "NO DEFINIDO"
        assert product.default_profit_margin == 0.06
        assert not product.image  # Verificar que el campo imagen está vacío


