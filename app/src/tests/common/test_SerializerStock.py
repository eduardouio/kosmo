import pytest
from decimal import Decimal
from datetime import date
from common.SerializerStock import SerializerStock
from products.models import StockDay, StockDetail, Product, BoxItems
from partners.models import Partner


@pytest.mark.django_db
class TestSerializerStock:

    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="TEST PARTNER",
            short_name="TP",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="PROVEEDOR",
            default_profit_margin=Decimal('0.10'),
            website="www.test.com",
            credit_term=30,
            skype="test_skype",
            email="test@partner.com",
            phone="0987654321"
        )

    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un stock day"""
        return StockDay.objects.create(
            date=date.today(),
            is_active=True
        )

    @pytest.fixture
    def product(self):
        """Fixture para crear un producto"""
        return Product.objects.create(
            name="ROSA TEST",
            variety="RED",
            colors="ROJO, ROSADO"
        )

    @pytest.fixture
    def stock_detail(self, stock_day, partner):
        """Fixture para crear un stock detail"""
        return StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner,
            quantity=10,
            box_model="HB",
            tot_stem_flower=250,
            tot_cost_price_box=Decimal('15.50'),
            profit_margin=Decimal('0.08')
        )

    @pytest.fixture
    def box_item(self, stock_detail, product):
        """Fixture para crear un box item"""
        return BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=40,  # Agregado campo requerido
            qty_stem_flower=25,
            stem_cost_price=Decimal('0.62'),
            total_bunches=1,
            stems_bunch=25
        )

    def test_serializer_stock_initialization(self):
        """Test que SerializerStock se puede inicializar"""
        serializer = SerializerStock()
        assert serializer is not None
        assert hasattr(serializer, 'get_line')

    def test_get_line_basic_structure(self, stock_detail):
        """Test estructura básica del método get_line"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        # Verificar que es un diccionario
        assert isinstance(result, dict)

        # Verificar campos principales
        required_fields = [
            'stock_detail_id', 'quantity', 'is_visible', 'is_selected',
            'is_in_order', 'box_model', 'tot_stem_flower',
            'tot_cost_price_box', 'id_user_created', 'is_active',
            'partner', 'box_items'
        ]

        for field in required_fields:
            assert field in result

    def test_get_line_stock_detail_fields(self, stock_detail):
        """Test campos del stock detail en la serialización"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        assert result['stock_detail_id'] == stock_detail.id
        assert result['quantity'] == stock_detail.quantity
        assert result['box_model'] == stock_detail.box_model
        assert result['tot_stem_flower'] == stock_detail.tot_stem_flower
        assert result['tot_cost_price_box'] == float(
            stock_detail.tot_cost_price_box
        )
        assert result['id_user_created'] == stock_detail.id_user_created
        assert result['is_active'] == stock_detail.is_active

    def test_get_line_default_boolean_fields(self, stock_detail):
        """Test campos booleanos por defecto"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        assert result['is_visible'] is True
        assert result['is_selected'] is False
        assert result['is_in_order'] is False

    def test_get_line_partner_structure(self, stock_detail):
        """Test estructura del partner en la serialización"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        partner_data = result['partner']
        assert isinstance(partner_data, dict)

        # Verificar campos del partner
        partner_fields = [
            'id', 'name', 'short_name', 'business_tax_id', 'address',
            'city', 'default_profit_margin', 'website', 'credit_term',
            'skype', 'email', 'phone', 'is_active'
        ]

        for field in partner_fields:
            assert field in partner_data

    def test_get_line_partner_data_accuracy(self, stock_detail):
        """Test exactitud de datos del partner"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        partner_data = result['partner']
        partner = stock_detail.partner

        assert partner_data['id'] == partner.id
        assert partner_data['name'] == partner.name
        assert partner_data['short_name'] == partner.short_name
        assert partner_data['business_tax_id'] == partner.business_tax_id
        assert partner_data['address'] == partner.address
        assert partner_data['city'] == partner.city
        assert partner_data['default_profit_margin'] == float(
            partner.default_profit_margin
        )
        assert partner_data['website'] == partner.website
        assert partner_data['credit_term'] == partner.credit_term
        assert partner_data['skype'] == partner.skype
        assert partner_data['email'] == partner.email
        assert partner_data['phone'] == partner.phone
        assert partner_data['is_active'] == partner.is_active

    def test_get_line_box_items_empty(self, stock_detail):
        """Test box_items cuando no hay items"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        assert isinstance(result['box_items'], list)
        assert len(result['box_items']) == 0

    def test_get_line_with_box_items(self, stock_detail, box_item):
        """Test serialización con box items"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_items = result['box_items']
        assert isinstance(box_items, list)
        assert len(box_items) == 1

        box_data = box_items[0]

        # Verificar campos del box item
        box_fields = [
            'id', 'stock_detail_id', 'product_id', 'product_name',
            'product_variety', 'product_image', 'product_colors'
        ]

        for field in box_fields:
            assert field in box_data

    def test_get_line_box_item_data_accuracy(self, stock_detail, box_item):
        """Test exactitud de datos del box item"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_data = result['box_items'][0]

        assert box_data['id'] == box_item.id
        assert box_data['stock_detail_id'] == box_item.stock_detail_id
        assert box_data['product_id'] == box_item.product_id
        assert box_data['product_name'] == box_item.product.name
        assert box_data['product_variety'] == box_item.product.variety

    def test_get_line_product_colors_parsing(self, stock_detail, box_item):
        """Test parsing de colores del producto"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_data = result['box_items'][0]
        colors = box_data['product_colors']

        assert isinstance(colors, list)
        # El producto tiene colors="ROJO, ROSADO"
        assert 'ROJO' in colors
        assert 'ROSADO' in colors

    def test_get_line_product_no_colors(self, stock_detail, product):
        """Test producto sin colores definidos"""
        # Modificar producto para no tener colores
        product.colors = None
        product.save()

        BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=40,  # Agregado campo requerido
            qty_stem_flower=25,
            stem_cost_price=Decimal('0.62'),
            total_bunches=1,
            stems_bunch=25
        )

        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_data = result['box_items'][0]
        colors = box_data['product_colors']

        assert colors == ['NO DEFINIDO']

    def test_get_line_product_empty_colors(self, stock_detail, product):
        """Test producto con colores vacíos"""
        # Modificar producto para tener colores vacíos
        product.colors = ""
        product.save()

        BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=40,  # Agregado campo requerido
            qty_stem_flower=25,
            stem_cost_price=Decimal('0.62'),
            total_bunches=1,
            stems_bunch=25
        )

        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_data = result['box_items'][0]
        colors = box_data['product_colors']

        assert colors == ['NO DEFINIDO']

    def test_get_line_product_image_handling(self, stock_detail, box_item):
        """Test manejo de imagen del producto"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_data = result['box_items'][0]

        # Sin imagen debería ser string vacío
        assert box_data['product_image'] == ''

    def test_get_line_multiple_box_items(self, stock_detail, product):
        """Test con múltiples box items"""
        # Crear múltiples box items
        for i in range(3):
            BoxItems.objects.create(
                stock_detail=stock_detail,
                product=product,
                length=40,  # Agregado campo requerido
                qty_stem_flower=25,
                stem_cost_price=Decimal('0.62'),
                total_bunches=1,
                stems_bunch=25
            )

        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        box_items = result['box_items']
        assert len(box_items) == 3

    def test_get_line_decimal_to_float_conversion(self, stock_detail):
        """Test conversión de Decimal a float"""
        serializer = SerializerStock()
        result = serializer.get_line(stock_detail)

        # tot_cost_price_box debe ser float, no Decimal
        assert isinstance(result['tot_cost_price_box'], float)
        assert result['tot_cost_price_box'] == 15.50

        # default_profit_margin del partner también debe ser float
        partner_data = result['partner']
        assert isinstance(partner_data['default_profit_margin'], float)
        assert partner_data['default_profit_margin'] == 0.10
