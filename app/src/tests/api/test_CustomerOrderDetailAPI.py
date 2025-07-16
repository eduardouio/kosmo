import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from products.models import Product, StockDay
from partners.models import Partner
from trade.models import (
    Order,
    OrderItems,
    OrderBoxItems
)


@pytest.mark.django_db
class TestCustomerOrderDetailAPI:

    def setup_method(self):
        """Configuración de datos de prueba antes de cada test"""
        self.client = Client()

        # Crear un partner/cliente de prueba
        test_customer_tax_id = f'TEST_CUSTOMER_{id(self)}'
        self.customer, created = Partner.objects.get_or_create(
            business_tax_id=test_customer_tax_id,
            defaults={
                'name': 'TEST CUSTOMER INC',
                'address': '123 TEST STREET',
                'country': 'ECUADOR',
                'city': 'QUITO',
                'credit_term': 30,
                'consolidate': False,
                'email': 'test@customer.com',
                'phone': '123456789',
                'type_partner': 'CLIENTE'
            }
        )

        # Crear un proveedor de prueba
        test_supplier_tax_id = f'TEST_SUPPLIER_{id(self)}'
        self.supplier, created = Partner.objects.get_or_create(
            business_tax_id=test_supplier_tax_id,
            defaults={
                'name': 'TEST SUPPLIER FLOWERS',
                'short_name': 'TSF',
                'address': 'TEST FARM ADDRESS',
                'city': 'TEST CITY',
                'credit_term': 45,
                'is_profit_margin_included': False,
                'default_profit_margin': Decimal('0.06'),
                'consolidate': False,
                'email': 'test@supplier.com',
                'phone': '987654321',
                'type_partner': 'PROVEEDOR'
            }
        )

        # Crear proveedor por defecto para tarifas generales
        self.default_supplier, created = Partner.objects.get_or_create(
            business_tax_id='9999999999',
            defaults={
                'name': 'TEST DEFAULT SUPPLIER',
                'address': 'TEST DEFAULT ADDRESS',
                'type_partner': 'PROVEEDOR'
            }
        )

        # Crear productos de prueba
        test_prefix = f'TEST_{id(self)}'
        self.product1, created = Product.objects.get_or_create(
            name=f'ROSA_{test_prefix}',
            variety='TEST_VARIETY_1',
            defaults={
                'colors': 'RED',
                'default_profit_margin': Decimal('0.06')
            }
        )

        self.product2, created = Product.objects.get_or_create(
            name=f'CLAVEL_{test_prefix}',
            variety='TEST_VARIETY_2',
            defaults={
                'colors': 'WHITE',
                'default_profit_margin': Decimal('0.06')
            }
        )

        # Crear StockDay de prueba
        self.stock_day, created = StockDay.objects.get_or_create(
            date=date.today(),
            defaults={'is_active': True}
        )

        # Crear orden de venta de prueba
        self.sales_order = Order.objects.create(
            serie='100',
            consecutive=1,
            stock_day=self.stock_day,
            partner=self.customer,
            type_document='ORD_VENTA',
            status='CONFIRMADO',
            total_price=Decimal('1000.00'),
            total_margin=Decimal('100.00'),
            qb_total=10,
            hb_total=5,
            eb_total=2,
            fb_total=Decimal('7.75'),
            total_stem_flower=500,
            total_bunches=50
        )

        # Crear orden de compra relacionada
        self.purchase_order = Order.objects.create(
            serie='200',
            consecutive=1,
            stock_day=self.stock_day,
            partner=self.supplier,
            parent_order=self.sales_order,
            type_document='ORD_COMPRA',
            status='CONFIRMADO',
            total_price=Decimal('900.00'),
            total_margin=Decimal('100.00')
        )

        # Crear items de orden
        self.order_item1 = OrderItems.objects.create(
            order=self.sales_order,
            box_model='QB',
            quantity=5,
            tot_stem_flower=250,
            line_price=Decimal('500.00'),
            line_margin=Decimal('50.00'),
            line_total=Decimal('550.00'),
            line_commission=Decimal('25.00'),
            total_bunches=25
        )

        self.order_item2 = OrderItems.objects.create(
            order=self.sales_order,
            box_model='HB',
            quantity=3,
            tot_stem_flower=150,
            line_price=Decimal('300.00'),
            line_margin=Decimal('30.00'),
            line_total=Decimal('330.00'),
            line_commission=Decimal('15.00'),
            total_bunches=15
        )

        # Crear box items para los order items
        self.order_box_item1 = OrderBoxItems.objects.create(
            order_item=self.order_item1,
            product=self.product1,
            length=50,
            qty_stem_flower=50,
            stems_bunch=25,
            total_bunches=2,
            stem_cost_price=Decimal('2.00'),
            profit_margin=Decimal('0.20')
        )

        self.order_box_item2 = OrderBoxItems.objects.create(
            order_item=self.order_item2,
            product=self.product2,
            length=60,
            qty_stem_flower=50,
            stems_bunch=25,
            total_bunches=2,
            stem_cost_price=Decimal('2.50'),
            profit_margin=Decimal('0.25')
        )

    def test_get_order_detail_success(self):
        """Test exitoso para obtener detalles de una orden"""
        url = reverse('customer-order-detail',
                      kwargs={'order_id': self.sales_order.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()

        # Verificar estructura de respuesta
        assert 'order' in data
        assert 'orderLines' in data
        assert 'customer' in data
        assert 'supplier' in data

        # Verificar datos de la orden
        order_data = data['order']
        assert order_data['id'] == self.sales_order.id
        assert order_data['serie'] == '100'
        # assert order_data['consecutive'] == '000001'
        assert order_data['type_document'] == 'ORD_VENTA'
        assert order_data['status'] == 'CONFIRMADO'
        assert float(order_data['total_price']) == 1000.00
        assert float(order_data['total_margin']) == 100.00
        assert order_data['qb_total'] == 10
        assert order_data['hb_total'] == 5
        assert order_data['eb_total'] == 2
        assert order_data['total_stem_flower'] == 500
        assert order_data['total_bunches'] == 50

        # Verificar líneas de orden
        order_lines = data['orderLines']
        assert len(order_lines) == 2

        # Verificar primera línea
        line1 = order_lines[0]
        assert line1['id'] == self.order_item1.id
        assert line1['box_model'] == 'QB'
        assert line1['quantity'] == 5
        assert line1['tot_stem_flower'] == 250
        assert float(line1['line_price']) == 500.00
        assert float(line1['line_margin']) == 50.00
        assert float(line1['line_total']) == 550.00
        assert line1['total_bunches'] == 25

        # Verificar box items de la primera línea
        box_items1 = line1['order_box_items']
        assert len(box_items1) == 1
        box_item1 = box_items1[0]
        assert box_item1['product']['name'] == self.product1.name
        assert box_item1['product']['variety'] == 'TEST_VARIETY_1'
        assert box_item1['length'] == 50
        assert box_item1['qty_stem_flower'] == 50
        assert box_item1['stems_bunch'] == 25
        assert box_item1['total_bunches'] == 2
        assert float(box_item1['stem_cost_price']) == 2.00
        assert float(box_item1['profit_margin']) == 0.20

        # Verificar datos del cliente
        customer_data = data['customer']
        assert customer_data['id'] == self.customer.id
        assert customer_data['name'] == 'TEST CUSTOMER INC'
        assert customer_data['business_tax_id'] == self.customer.business_tax_id
        assert customer_data['address'] == '123 TEST STREET'
        assert customer_data['country'] == 'ECUADOR'
        assert customer_data['city'] == 'QUITO'
        assert customer_data['credit_term'] == 30
        assert customer_data['email'] == 'test@customer.com'
        assert customer_data['phone'] == '123456789'

        # Verificar datos del proveedor
        supplier_data = data['supplier']
        assert supplier_data['id'] == self.supplier.id
        assert supplier_data['name'] == 'TEST SUPPLIER FLOWERS'
        assert supplier_data['short_name'] == 'TSF'
        assert supplier_data['business_tax_id'] == self.supplier.business_tax_id
        assert supplier_data['address'] == 'TEST FARM ADDRESS'
        assert supplier_data['city'] == 'TEST CITY'
        assert supplier_data['credit_term'] == 45
        assert supplier_data['email'] == 'test@supplier.com'
        assert supplier_data['phone'] == '987654321'

    def test_get_order_detail_not_found(self):
        """Test para orden no encontrada"""
        url = reverse('customer-order-detail', kwargs={'order_id': 99999})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_get_order_detail_inactive_order(self):
        """Test para orden inactiva"""
        # Desactivar la orden
        self.sales_order.is_active = False
        self.sales_order.save()

        url = reverse('customer-order-detail',
                      kwargs={'order_id': self.sales_order.id})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_get_order_detail_with_default_supplier(self):
        """Test para orden sin proveedor específico (usa proveedor por defecto)"""
        # Eliminar la orden de compra relacionada
        self.purchase_order.delete(id=self.purchase_order.id)

        url = reverse('customer-order-detail',
                      kwargs={'order_id': self.sales_order.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()
        supplier_data = data['supplier']

        # Debe usar el proveedor por defecto
        assert supplier_data['business_tax_id'] == '9999999999'
        assert supplier_data['name'] == 'TEST DEFAULT SUPPLIER'

    def test_get_order_detail_purchase_order(self):
        """Test para orden de compra"""
        url = reverse('customer-order-detail',
                      kwargs={'order_id': self.purchase_order.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()
        order_data = data['order']

        assert order_data['type_document'] == 'ORD_COMPRA'
        assert float(order_data['total_price']) == 900.00

    def teardown_method(self):
        """Limpieza después de cada test"""
        # Los objetos se limpian automáticamente por @pytest.mark.django_db
        pass
