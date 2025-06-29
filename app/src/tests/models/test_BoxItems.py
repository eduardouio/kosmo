import pytest
from datetime import date, timedelta
import random
from products.models import BoxItems, StockDetail, StockDay, Product
from partners.models import Partner


@pytest.mark.django_db
class TestBoxItems:
    
    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un stock day"""
        # Usar una fecha aleatoria para evitar conflictos
        base_date = date(2024, 1, 1)
        random_days = random.randint(1, 365)
        unique_date = base_date + timedelta(days=random_days)
        return StockDay.objects.create(date=unique_date)
    
    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return Partner.objects.create(
            business_tax_id=f"123456789{unique_id[:1]}",
            name=f"TEST PARTNER {unique_id}",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR"
        )
        
    @pytest.fixture
    def product(self):
        """Fixture para crear un producto"""
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        return Product.objects.create(
            name=f"Rosa_{unique_id}",
            variety=f"Explorer_{unique_id}"
        )
        
    @pytest.fixture
    def stock_detail(self, stock_day, partner):
        """Fixture para crear un stock detail"""
        return StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            box_model="HB"
        )
        
    def test_create_box_item(self, stock_detail, product):
        """Test creación de box item"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            qty_stem_flower=25,
            stem_cost_price=0.45,
            profit_margin=0.08,
            total_bunches=5,
            stems_bunch=5
        )
        assert box_item.stock_detail == stock_detail
        assert box_item.product == product
        assert box_item.length == 50
        assert box_item.qty_stem_flower == 25
        assert box_item.stem_cost_price == 0.45
        assert box_item.profit_margin == 0.08
        assert box_item.total_bunches == 5
        assert box_item.stems_bunch == 5
        
    def test_default_values(self, stock_detail, product):
        """Test valores por defecto"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=0.45
        )
        assert box_item.qty_stem_flower == 0
        assert box_item.profit_margin == 0.06
        assert box_item.total_bunches == 0
        assert box_item.stems_bunch == 0
        
    def test_get_box_items(self, stock_detail, product):
        """Test método classmethod get_box_items"""
        box_item1 = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=40,
            stem_cost_price=0.40
        )
        
        # Crear otro producto para la misma caja
        import uuid
        unique_id2 = str(uuid.uuid4())[:8]
        product2 = Product.objects.create(
            name=f"Clavel_{unique_id2}",
            variety=f"Standard_{unique_id2}"
        )
        box_item2 = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product2,
            length=50,
            stem_cost_price=0.35
        )
        
        # Crear box item inactivo (no debería aparecer)
        inactive_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=60,
            stem_cost_price=0.50
        )
        inactive_item.is_active = False
        inactive_item.save()
        
        box_items = BoxItems.get_box_items(stock_detail)
        assert box_item1 in box_items
        assert box_item2 in box_items
        assert inactive_item not in box_items
        assert box_items.count() == 2
        
    def test_str_method(self, stock_detail, product):
        """Test método __str__"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=0.45
        )
        assert str(box_item) == product.name
        
    def test_foreign_key_cascade(self, stock_detail, product):
        """Test cascade al eliminar stock_detail o product"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=0.45
        )
        
        box_item_id = box_item.id
        
        # Eliminar stock_detail debería eliminar box_item por CASCADE
        # Usar el delete() de Django, no del BaseModel
        StockDetail.objects.filter(id=stock_detail.id).delete()
        
        with pytest.raises(BoxItems.DoesNotExist):
            BoxItems.objects.get(id=box_item_id)
            
    def test_positive_length_field(self, stock_detail, product):
        """Test que length es PositiveSmallIntegerField"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=0.45
        )
        assert box_item.length > 0
        assert isinstance(box_item.length, int)
        
    def test_decimal_fields_precision(self, stock_detail, product):
        """Test precisión de campos decimales"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=12.34,  # Valores que respetan decimales definidos
            profit_margin=0.12      # Valores que respetan decimales definidos
        )
        assert box_item.stem_cost_price == 12.34
        assert box_item.profit_margin == 0.12
        
    def test_optional_fields_null(self, stock_detail, product):
        """Test que campos opcionales pueden ser null"""
        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=50,
            stem_cost_price=0.45
            # No especificamos total_bunches ni stems_bunch
        )
        assert box_item.total_bunches == 0  # Valor por defecto
        assert box_item.stems_bunch == 0    # Valor por defecto
