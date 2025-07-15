import pytest
import json
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
        
        # Crear un partner/cliente de prueba
        self.customer = Partner.objects.create(
            business_tax_id='390486452',
            name='Ecuador Direct Roses',
            address='1500 Weston Rd Ste 214, Weston, Fl. 33326',
            country='Estados Unidos',
            city='Weston',
            credit_term=30,
            consolidate=False,
            email='compras@ecuadordirectroses.com',
            phone='',
            type_partner='CLIENTE'
        )
        
        # Crear productos de prueba
        self.product1 = Product.objects.create(
            name='ROSA',
            variety='AKITO',
            colors='WHITE AND CREAM',
            default_profit_margin=0.06
        )
        
        self.product2 = Product.objects.create(
            name='ROSA',
            variety='VENDELA',
            colors='WHITE AND CREAM',
            default_profit_margin=0.06
        )
        
        # Crear StockDay de prueba
        from datetime import date
        self.stock_day = StockDay.objects.create(
            date=date.today()
        )
        
    def test_create_order_success(self):
        """Test exitoso de creación de orden"""
        order_data = {
            'customer': {
                'id': self.customer.id
            },
            'stock_day': {
                'id': self.stock_day.id
            },
            'order_detail': [
                {
                    'stock_detail_id': 1,
                    'box_model': 'QB',
                    'quantity': 1,
                    'box_items': [
                        {
                            'product_id': self.product1.id,
                            'qty_stem_flower': 625,
                            'length': 50,
                            'stem_cost_price': 0.36,
                            'margin': 0.02,
                            'total_bunches': 25,
                            'stems_bunch': 25
                        },
                        {
                            'product_id': self.product2.id,
                            'qty_stem_flower': 600,
                            'length': 80,
                            'stem_cost_price': 0.96,
                            'margin': 0.25,
                            'total_bunches': 30,
                            'stems_bunch': 20
                        }
                    ]
                }
            ]
        }
        
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
        assert response_data['order']['status'] == 'PENDIENTE'
        
        # Verificar que se creó en la base de datos
        order = Order.objects.get(id=response_data['order']['id'])
        assert order.partner == self.customer
        assert order.stock_day == self.stock_day
        assert order.type_document == 'ORD_VENTA'
        
        # Verificar order items
        order_items = OrderItems.objects.filter(order=order)
        assert order_items.count() == 1
        
        order_item = order_items.first()
        assert order_item.box_model == 'QB'
        assert order_item.quantity == 1
        
        # Verificar box items
        box_items = OrderBoxItems.objects.filter(order_item=order_item)
        assert box_items.count() == 2
        
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
        
    def test_create_order_with_multiple_order_items(self):
        """Test con múltiples items de orden"""
        order_data = {
            'customer': {
                'id': self.customer.id
            },
            'stock_day': {
                'id': self.stock_day.id
            },
            'order_detail': [
                {
                    'stock_detail_id': 1,
                    'box_model': 'QB',
                    'quantity': 2,
                    'box_items': [
                        {
                            'product_id': self.product1.id,
                            'qty_stem_flower': 500,
                            'length': 60,
                            'stem_cost_price': 0.40,
                            'margin': 0.05,
                            'total_bunches': 20,
                            'stems_bunch': 25
                        }
                    ]
                },
                {
                    'stock_detail_id': 2,
                    'box_model': 'HB',
                    'quantity': 1,
                    'box_items': [
                        {
                            'product_id': self.product2.id,
                            'qty_stem_flower': 300,
                            'length': 70,
                            'stem_cost_price': 1.00,
                            'margin': 0.30,
                            'total_bunches': 15,
                            'stems_bunch': 20
                        }
                    ]
                }
            ]
        }
        
        response = self.client.post(
            reverse('create_order'),
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        response_data = response.json()
        order = Order.objects.get(id=response_data['order']['id'])
        
        # Verificar que se crearon múltiples order items
        order_items = OrderItems.objects.filter(order=order)
        assert order_items.count() == 2
        
        # Verificar que los totales se calcularon correctamente
        assert order.qb_total > 0 or order.hb_total > 0
    