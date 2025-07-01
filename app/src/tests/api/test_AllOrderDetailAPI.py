import pytest
import json
from django.urls import reverse
from django.test import Client
from datetime import date, datetime
from decimal import Decimal

from accounts.models import CustomUserModel
from products.models import StockDay, StockDetail, Product, BoxItems
from partners.models import Partner, Contact
from trade.models import Order, OrderItems, OrderBoxItems


@pytest.mark.django_db
class TestAllOrderDetailAPI:

    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )

    @pytest.fixture
    def client_logged(self, user):
        """Fixture para cliente autenticado"""
        client = Client()
        client.force_login(user)
        return client

    @pytest.fixture
    def partner_customer(self):
        """Fixture para crear un partner cliente"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="CLIENTE TEST",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )

    @pytest.fixture
    def partner_supplier(self):
        """Fixture para crear un partner proveedor"""
        return Partner.objects.create(
            business_tax_id="0987654321",
            name="PROVEEDOR TEST",
            address="Av. Test 456",
            country="Ecuador",
            city="Guayaquil",
            type_partner="PROVEEDOR"
        )

    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un StockDay"""
        return StockDay.objects.create(
            date=date.today(),
            is_active=True
        )

    @pytest.fixture
    def stock_detail(self, stock_day, partner_supplier):
        """Fixture para crear un StockDetail"""
        return StockDetail.objects.create(
            stock_day=stock_day,
            partner=partner_supplier,
            quantity=5,
            box_model="HB",
            tot_stem_flower=125,
            tot_cost_price_box=Decimal("5.50"),
            profit_margin=Decimal("0.08")
        )

    @pytest.fixture
    def product(self):
        """Fixture para crear un producto"""
        return Product.objects.create(
            name="ROSA ROJA",
            variety="RED NAOMI",
            colors="ROJO",
            default_profit_margin=Decimal("0.06"),
            notes="Producto de prueba"
        )

    @pytest.fixture
    def box_items(self, stock_detail, product):
        """Fixture para crear box items"""
        return BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=60,
            qty_stem_flower=25,
            stem_cost_price=Decimal("0.22"),
            profit_margin=Decimal("0.06"),
            total_bunches=1,
            stems_bunch=25
        )

    @pytest.fixture
    def contact(self, partner_customer):
        """Fixture para crear un contacto principal"""
        return Contact.objects.create(
            partner=partner_customer,
            name="Juan Pérez",
            position="Gerente",
            contact_type="PRINCIPAL",
            phone="0991234567",
            email="juan@test.com",
            is_principal=True
        )

    @pytest.fixture
    def order_sale(self, partner_customer, stock_day):
        """Fixture para crear una orden de venta"""
        return Order.objects.create(
            partner=partner_customer,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            serie="200",
            consecutive=1,
            total_price=Decimal("100.00"),
            total_margin=Decimal("10.00"),
            qb_total=0,
            hb_total=5,
            total_stem_flower=125,
            total_bunches=5
        )

    @pytest.fixture
    def order_purchase(self, partner_supplier, stock_day, order_sale):
        """Fixture para crear una orden de compra"""
        return Order.objects.create(
            partner=partner_supplier,
            stock_day=stock_day,
            type_document="ORD_COMPRA",
            status="PENDIENTE",
            serie="100",
            consecutive=1,
            parent_order=order_sale,
            total_price=Decimal("80.00"),
            total_margin=Decimal("8.00"),
            qb_total=0,
            hb_total=5,
            total_stem_flower=125,
            total_bunches=5
        )

    @pytest.fixture
    def order_item(self, order_sale, stock_detail):
        """Fixture para crear un order item"""
        return OrderItems.objects.create(
            order=order_sale,
            id_stock_detail=stock_detail.id,
            box_model="HB",
            quantity=5,
            line_price=Decimal("20.00"),
            line_margin=Decimal("2.00"),
            line_total=Decimal("100.00"),
            tot_stem_flower=125
        )

    @pytest.fixture
    def order_box_item(self, order_item, product):
        """Fixture para crear un order box item"""
        return OrderBoxItems.objects.create(
            order_item=order_item,
            product=product,
            length=60,
            qty_stem_flower=25,
            stem_cost_price=Decimal("0.22"),
            profit_margin=Decimal("0.06"),
            total_bunches=1,
            stems_bunch=25
        )

    def test_get_sales_orders_success(
        self, client_logged, stock_day, order_sale, order_item, 
        order_box_item, contact
    ):
        """Test para obtener órdenes de venta exitosamente"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Verificar que retorna una lista
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Verificar estructura de la orden
        order_data = data[0]
        assert 'order' in order_data
        assert 'order_details' in order_data
        assert 'is_selected' in order_data
        assert 'is_modified' in order_data
        assert 'is_cancelled' in order_data
        assert 'is_confirmed' in order_data
        assert 'is_invoiced' in order_data
        
        # Verificar datos de la orden
        assert order_data['order']['id'] == order_sale.id
        assert order_data['order']['type_document'] == "ORD_VENTA"
        assert order_data['order']['status'] == "PENDIENTE"
        assert order_data['order']['total_price'] == 100.00
        assert order_data['order']['hb_total'] == 5
        assert order_data['order']['total_stem_flower'] == 125
        
        # Verificar datos del partner con contacto
        partner_data = order_data['order']['partner']
        assert partner_data['id'] == order_sale.partner.id
        assert partner_data['name'] == "CLIENTE TEST"
        assert 'contact' in partner_data
        assert partner_data['contact']['name'] == "JUAN PÉREZ"
        assert partner_data['contact']['is_principal'] is True

    def test_get_purchase_orders_success(
        self, client_logged, stock_day, order_purchase, order_sale
    ):
        """Test para obtener órdenes de compra exitosamente"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=purchase'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Verificar que retorna una lista
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Verificar estructura de la orden
        order_data = data[0]
        assert order_data['order']['id'] == order_purchase.id
        assert order_data['order']['type_document'] == "ORD_COMPRA"
        assert order_data['order']['parent_order']['id'] == order_sale.id

    def test_get_orders_no_results(self, client_logged):
        """Test cuando no hay órdenes para el stock_day"""
        # Crear un stock_day que no tiene órdenes
        stock_day_empty = StockDay.objects.create(
            date=date(2024, 1, 15),
            is_active=True
        )
        
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day_empty.id})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Verificar que retorna una lista vacía
        assert isinstance(data, list)
        assert data == []

    def test_get_orders_with_null_stock_detail(
        self, client_logged, stock_day, order_sale, partner_customer
    ):
        """Test cuando un order item tiene stock_detail nulo"""
        # Crear un order item con stock_detail inexistente
        order_item_null = OrderItems.objects.create(
            order=order_sale,
            id_stock_detail=99999,  # ID que no existe
            box_model="HB",
            quantity=3,
            line_price=Decimal("15.00"),
            line_margin=Decimal("1.50"),
            line_total=Decimal("45.00"),
            tot_stem_flower=75
        )
        
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        # No debería fallar, debería manejar el caso elegantemente
        assert response.status_code == 200
        data = json.loads(response.content)
        
        assert isinstance(data, list)
        assert len(data) == 1
        
        # Verificar que los order_details contienen el item con stock_detail nulo
        order_details = data[0]['order_details']
        assert len(order_details) == 1
        
        # Verificar que se maneja correctamente el partner nulo
        partner_info = order_details[0]['partner']['partner']
        assert partner_info['name'] == 'Stock no encontrado'
        assert partner_info['id'] is None

    def test_get_orders_without_contact(
        self, client_logged, stock_day, order_sale, order_item, order_box_item
    ):
        """Test cuando el partner no tiene contacto principal"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Verificar que el contacto está vacío
        partner_data = data[0]['order']['partner']
        assert partner_data['contact'] == {}

    def test_get_orders_with_parent_order(
        self, client_logged, stock_day, order_purchase, order_sale
    ):
        """Test verificar que se incluye la información de parent_order"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=purchase'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Verificar parent_order
        parent_order_data = data[0]['order']['parent_order']
        assert parent_order_data['id'] == order_sale.id
        assert parent_order_data['customer'] == order_sale.partner.name
        assert parent_order_data['total_price'] == float(order_sale.total_price)
        assert parent_order_data['status'] == order_sale.status

    def test_get_orders_default_type(
        self, client_logged, stock_day, order_purchase
    ):
        """Test que por defecto retorna órdenes de compra cuando no se especifica type"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Por defecto debería retornar órdenes de venta
        # (cuando no se especifica type)
        assert len(data) == 1
        assert data[0]['order']['type_document'] == "ORD_VENTA"

    def test_order_status_flags(
        self, client_logged, stock_day, partner_customer
    ):
        """Test verificar los flags de estado de las órdenes"""
        # Orden cancelada
        order_cancelled = Order.objects.create(
            partner=partner_customer,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CANCELADO",
            serie="200",
            consecutive=2
        )
        
        # Orden confirmada
        order_confirmed = Order.objects.create(
            partner=partner_customer,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CONFIRMADO",
            serie="200",
            consecutive=3
        )
        
        # Orden facturada
        order_invoiced = Order.objects.create(
            partner=partner_customer,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="PENDIENTE",
            serie="200",
            consecutive=4,
            is_invoiced=True,
            id_invoice=123
        )
        
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': stock_day.id})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        assert response.status_code == 200
        data = json.loads(response.content)
        
        # Buscar cada orden en la respuesta
        orders_by_id = {order['order']['id']: order for order in data}
        
        # Verificar flags de orden cancelada
        cancelled_order = orders_by_id[order_cancelled.id]
        assert cancelled_order['is_cancelled'] is True
        assert cancelled_order['is_confirmed'] is False
        
        # Verificar flags de orden confirmada
        confirmed_order = orders_by_id[order_confirmed.id]
        assert confirmed_order['is_cancelled'] is False
        assert confirmed_order['is_confirmed'] is True
        
        # Verificar flags de orden facturada
        invoiced_order = orders_by_id[order_invoiced.id]
        assert invoiced_order['is_invoiced'] is True
        assert invoiced_order['is_confirmed'] is True  # Las facturadas se consideran confirmadas
        assert invoiced_order['id_invoice'] == 123

    def test_url_pattern(self, client_logged, stock_day):
        """Test que la URL funciona correctamente"""
        # Test con diferentes parámetros
        urls_to_test = [
            f'/api/orders/by_stock_day/{stock_day.id}/',
            f'/api/orders/by_stock_day/{stock_day.id}/?type=sale',
            f'/api/orders/by_stock_day/{stock_day.id}/?type=purchase',
        ]
        
        for url in urls_to_test:
            response = client_logged.get(url)
            assert response.status_code == 200

    def test_invalid_stock_day_id(self, client_logged):
        """Test con ID de stock_day inválido"""
        url = reverse('order_detail_by_stock_day', kwargs={'id_stock_day': 99999})
        url += '?type=sale'
        
        response = client_logged.get(url)
        
        # Debería retornar 200 con data vacía
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data == []
