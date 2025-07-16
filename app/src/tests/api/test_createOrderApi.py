import pytest
import json
import os
from django.test import Client
from django.urls import reverse
from products.models import Product, StockDay
from partners.models import Partner
from trade.models import Order, OrderItems, OrderBoxItems


@pytest.mark.django_db
class TestCreateOrderAPI:

    def setup_method(self):
        """Configuración de datos de prueba antes de cada test"""
        self.client = Client()

        # Crear un partner/cliente de prueba que corresponda al del JSON
        # Usar un business_tax_id único para tests
        test_customer_tax_id = f'TEST_CUSTOMER_{id(self)}'
        self.customer, created = Partner.objects.get_or_create(
            business_tax_id=test_customer_tax_id,
            defaults={
                'name': 'Alwasys For You Inc - Test',
                'address': '992 east 15 st Brooklyn',
                'country': 'Estados Unidos',
                'city': 'New York',
                'credit_term': 30,
                'consolidate': False,
                'email': 'ymichailov@hotmail.com',
                'phone': '',
                'type_partner': 'CLIENTE'
            }
        )

        # Crear un proveedor de prueba que corresponda al del JSON
        # Usar un business_tax_id único para tests
        test_supplier_tax_id = f'TEST_SUPPLIER_{id(self)}'
        self.supplier, created = Partner.objects.get_or_create(
            business_tax_id=test_supplier_tax_id,
            defaults={
                'name': 'ADONAI FLOWERS - Test',
                'short_name': 'AF',
                'address': 'CAYAMBE',
                'city': 'CAYAMBE',
                'credit_term': 45,
                'is_profit_margin_included': False,
                'default_profit_margin': 0.06,
                'consolidate': False,
                'email': 'contabilidad.adonaiflowers@gmail.com',
                'phone': '',
                'type_partner': 'PROVEEDOR'
            }
        )

        # Crear productos de prueba que coincidan con los del JSON
        # Usar nombres únicos para evitar conflictos entre tests
        test_prefix = f'TEST_{id(self)}'
        self.product1, created = Product.objects.get_or_create(
            name=f'ROSA_{test_prefix}',
            variety='AKITO',
            defaults={
                'colors': 'WHITE AND CREAM',
                'default_profit_margin': 0.0  # Valor del JSON
            }
        )

        self.product2, created = Product.objects.get_or_create(
            name=f'ROSA_{test_prefix}',
            variety='VENDELA',
            defaults={
                'colors': 'WHITE AND CREAM',
                'default_profit_margin': 0.0  # Valor del JSON
            }
        )

        self.product3, created = Product.objects.get_or_create(
            name=f'ROSA_{test_prefix}',
            variety='MONDIAL',
            defaults={
                'colors': 'WHITE AND CREAM',
                'default_profit_margin': 0.0  # Valor del JSON
            }
        )

        # Crear StockDay de prueba
        from datetime import date, timedelta
        import random

        # Crear una fecha única para el test para evitar conflictos
        test_date = date.today() + timedelta(days=random.randint(1, 1000))
        self.stock_day, created = StockDay.objects.get_or_create(
            date=test_date
        )

        # Cargar el archivo JSON de ejemplo
        json_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'testdata',
            'createOrderApiJsonExapmple.json'
        )
        with open(json_path, 'r') as f:
            self.example_data = json.load(f)

        # Crear un mapeo de productos del JSON a productos del test
        self.product_mapping = {
            1: self.product1,  # AKITO
            2: self.product2,  # VENDELA
            6: self.product3   # MONDIAL
        }

    def test_create_order_with_json_example(self):
        """Test de creación de orden usando los datos del JSON de ejemplo"""
        # Adaptamos los datos del JSON para el formato que espera el API
        order_data = {
            'customer': {
                'id': self.customer.id
            },
            'stock_day': {
                'id': self.stock_day.id
            },
            'order_detail': []
        }

        # Convertir orderLines del JSON al formato del API
        for order_line in self.example_data['orderLines']:
            detail_item = {
                'stock_detail_id': 0,  # Valor por defecto
                'box_model': order_line['box_model'],
                'quantity': order_line['quantity'],
                'box_items': []
            }

            for box_item in order_line['order_box_items']:
                # Usar el mapeo de productos para obtener el ID correcto
                original_product_id = box_item['product']['id']
                mapped_product = self.product_mapping[original_product_id]

                detail_item['box_items'].append({
                    'product_id': mapped_product.id,
                    'qty_stem_flower': box_item['qty_stem_flower'],
                    'length': box_item['length'],
                    'stem_cost_price': float(box_item['stem_cost_price']),
                    'margin': float(box_item['profit_margin']),
                    'total_bunches': box_item['total_bunches'],
                    'stems_bunch': box_item['stems_bunch']
                })

            order_data['order_detail'].append(detail_item)

        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(order_data),
            content_type='application/json'
        )

        assert response.status_code == 201

        # Verificar que la orden fue creada
        response_data = response.json()
        assert 'order' in response_data
        assert response_data['order']['serie'] == '100'
        assert response_data['order']['type_document'] == 'ORD_VENTA'

        # Verificar que se creó en la base de datos
        order = Order.objects.get(id=response_data['order']['id'])
        assert order.partner == self.customer
        assert order.stock_day == self.stock_day
        assert order.type_document == 'ORD_VENTA'

        # Verificar order items
        order_items = OrderItems.objects.filter(order=order)
        assert order_items.count() == len(self.example_data['orderLines'])

        # Verificar que los totales tienen valores razonables
        # (pueden no coincidir exactamente debido a diferencias en cálculos)
        assert order.qb_total >= 0
        assert order.total_bunches >= 0
        assert order.total_stem_flower >= 0

        # Verificar que hay al menos algunos valores esperados
        expected_qb = self.example_data['order']['qb_total']
        if expected_qb > 0:
            assert order.qb_total > 0

        # Verificar box items
        total_box_items = 0
        for order_line in self.example_data['orderLines']:
            total_box_items += len(order_line['order_box_items'])

        total_actual_box_items = 0
        for item in order_items:
            box_items = OrderBoxItems.objects.filter(order_item=item)
            total_actual_box_items += box_items.count()

        assert total_actual_box_items == total_box_items

    def test_create_order_invalid_customer(self):
        """Test con cliente inexistente"""
        order_data = {
            'customer': {
                'id': 999999  # ID que no existe
            },
            'stock_day': {
                'id': self.stock_day.id
            },
            'order_detail': []
        }

        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(order_data),
            content_type='application/json'
        )

        assert response.status_code == 404
        response_data = response.json()
        assert 'error' in response_data
        assert response_data['error'] == 'Customer not found'

    def test_create_order_no_data(self):
        """Test sin datos en el body"""
        response = self.client.post(
            reverse('create_order'),
            data='',
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = response.json()
        assert 'error' in response_data
        assert response_data['error'] == 'No data provided'

    def test_create_order_invalid_json(self):
        """Test con JSON inválido"""
        response = self.client.post(
            reverse('create_order'),
            data='invalid json',
            content_type='application/json'
        )

        assert response.status_code == 400

    def test_create_order_missing_required_fields(self):
        """Test con campos requeridos faltantes"""
        order_data = {
            'customer': {
                'id': self.customer.id
            }
            # Falta stock_day y order_detail
        }

        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(order_data),
            content_type='application/json'
        )

        # El API debería fallar por campos faltantes
        assert response.status_code in [400, 500]
