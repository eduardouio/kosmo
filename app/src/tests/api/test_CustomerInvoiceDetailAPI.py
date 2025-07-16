import pytest
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from products.models import Product, StockDay
from partners.models import Partner
from trade.models import (
    Order,
    OrderItems,
    OrderBoxItems,
    Invoice,
    InvoiceItems,
    InvoiceBoxItems
)


@pytest.mark.django_db
class TestCustomerInvoiceDetailAPI:

    def setup_method(self):
        """Configuración de datos de prueba antes de cada test"""
        self.client = Client()

        # Crear un partner/cliente de prueba
        test_customer_tax_id = f'TEST_CUSTOMER_{id(self)}'
        self.customer, created = Partner.objects.get_or_create(
            business_tax_id=test_customer_tax_id,
            defaults={
                'name': 'Test Customer Inc',
                'address': '123 Test Street',
                'country': 'Ecuador',
                'city': 'Quito',
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
                'name': 'Test Supplier Flowers',
                'short_name': 'TSF',
                'address': 'Test Farm Address',
                'city': 'Test City',
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
                'name': 'Default Supplier',
                'address': 'Default Address',
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

        # Crear factura de venta
        self.invoice = Invoice.objects.create(
            order=self.sales_order,
            partner=self.customer,
            serie='100',
            consecutive=1,
            num_invoice='100-000001',
            type_document='FAC_VENTA',
            date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status='PENDIENTE',
            total_price=Decimal('1000.00'),
            total_margin=Decimal('100.00'),
            comision_seler=Decimal('50.00'),
            qb_total=10,
            hb_total=5,
            eb_total=2,
            fb_total=Decimal('7.75'),
            tot_stem_flower=500,
            total_bunches=50,
            awb='TEST-AWB-123',
            dae_export='TEST-DAE-456',
            hawb='TEST-HAWB-789',
            cargo_agency='Test Cargo',
            delivery_date=date.today() + timedelta(days=7),
            weight=Decimal('45.50')
        )

        # Crear items de factura
        self.invoice_item1 = InvoiceItems.objects.create(
            invoice=self.invoice,
            id_order_item=1,
            box_model='QB',
            quantity=5,
            tot_stem_flower=250,
            line_price=Decimal('500.00'),
            line_margin=Decimal('50.00'),
            line_total=Decimal('550.00'),
            line_commission=Decimal('25.00'),
            total_bunches=25
        )

        self.invoice_item2 = InvoiceItems.objects.create(
            invoice=self.invoice,
            id_order_item=2,
            box_model='HB',
            quantity=3,
            tot_stem_flower=150,
            line_price=Decimal('300.00'),
            line_margin=Decimal('30.00'),
            line_total=Decimal('330.00'),
            line_commission=Decimal('15.00'),
            total_bunches=15
        )

        # Crear box items para los invoice items
        self.invoice_box_item1 = InvoiceBoxItems.objects.create(
            invoice_item=self.invoice_item1,
            product=self.product1,
            length=50,
            qty_stem_flower=50,
            stems_bunch=25,
            total_bunches=2,
            stem_cost_price=Decimal('2.00'),
            profit_margin=Decimal('0.20')
        )

        self.invoice_box_item2 = InvoiceBoxItems.objects.create(
            invoice_item=self.invoice_item2,
            product=self.product2,
            length=60,
            qty_stem_flower=50,
            stems_bunch=25,
            total_bunches=2,
            stem_cost_price=Decimal('2.50'),
            profit_margin=Decimal('0.25')
        )

    def test_get_invoice_detail_success(self):
        """Test exitoso para obtener detalles de una factura"""
        url = reverse('customer-invoice-detail',
                      kwargs={'invoice_id': self.invoice.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()

        # Verificar estructura de respuesta
        assert 'invoice' in data
        assert 'invoiceLines' in data
        assert 'customer' in data
        assert 'supplier' in data

        # Verificar datos de la factura
        invoice_data = data['invoice']
        assert invoice_data['id'] == self.invoice.id
        assert invoice_data['serie'] == '100'
        assert invoice_data['consecutive'] == '000001'
        assert invoice_data['num_invoice'] == '100-000001'
        assert invoice_data['type_document'] == 'FAC_VENTA'
        assert invoice_data['type_document'] == 'FAC_VENTA'
        assert invoice_data['status'] == 'PENDIENTE'
        assert float(invoice_data['total_price']) == 1000.00
        assert float(invoice_data['total_margin']) == 100.00
        assert invoice_data['qb_total'] == 10
        assert invoice_data['hb_total'] == 5
        assert invoice_data['eb_total'] == 2
        assert invoice_data['tot_stem_flower'] == 500
        assert invoice_data['total_bunches'] == 50
        assert invoice_data['awb'] == 'TEST-AWB-123'
        assert invoice_data['dae_export'] == 'TEST-DAE-456'
        assert invoice_data['hawb'] == 'TEST-HAWB-789'
        assert invoice_data['cargo_agency'] == 'TEST CARGO'
        assert float(invoice_data['weight']) == 45.50

        # Verificar líneas de factura
        invoice_lines = data['invoiceLines']
        assert len(invoice_lines) == 2

        # Verificar primera línea
        line1 = invoice_lines[0]
        assert line1['id_order_item'] == 1
        assert line1['box_model'] == 'QB'
        assert line1['quantity'] == 5
        assert line1['tot_stem_flower'] == 250
        assert float(line1['line_price']) == 500.00
        assert float(line1['line_margin']) == 50.00
        assert float(line1['line_total']) == 550.00
        assert line1['total_bunches'] == 25

        # Verificar box items de la primera línea
        box_items1 = line1['invoice_box_items']
        assert len(box_items1) == 1
        box_item1 = box_items1[0]
        assert box_item1['product']['name'] == f'ROSA_TEST_{id(self)}'
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
        assert customer_data['business_tax_id'] == f'TEST_CUSTOMER_{id(self)}'
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
        assert supplier_data['business_tax_id'] == f'TEST_SUPPLIER_{id(self)}'
        assert supplier_data['address'] == 'TEST FARM ADDRESS'
        assert supplier_data['city'] == 'TEST CITY'
        assert supplier_data['credit_term'] == 45
        assert supplier_data['email'] == 'test@supplier.com'
        assert supplier_data['phone'] == '987654321'

    def test_get_invoice_detail_not_found(self):
        """Test para factura no encontrada"""
        url = reverse('customer-invoice-detail', kwargs={'invoice_id': 99999})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_get_invoice_detail_inactive_invoice(self):
        """Test para factura inactiva"""
        # Desactivar la factura
        self.invoice.is_active = False
        self.invoice.save()

        url = reverse('customer-invoice-detail',
                      kwargs={'invoice_id': self.invoice.id})
        response = self.client.get(url)

        assert response.status_code == 404

    def test_get_invoice_detail_with_default_supplier(self):
        """Test para factura sin proveedor específico (usa proveedor por defecto)"""
        # Eliminar la orden de compra relacionada
        self.purchase_order.delete(id=self.purchase_order.id)

        url = reverse('customer-invoice-detail',
                      kwargs={'invoice_id': self.invoice.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()
        supplier_data = data['supplier']

        # Debe usar el proveedor por defecto
        assert supplier_data['business_tax_id'] == '9999999999'
        assert supplier_data['name'] == 'DEFAULT SUPPLIER'

    def test_get_invoice_detail_purchase_invoice(self):
        """Test para factura de compra"""
        # Crear factura de compra
        purchase_invoice = Invoice.objects.create(
            order=self.purchase_order,
            partner=self.supplier,
            serie='200',
            consecutive=1,
            num_invoice='200-000001',
            type_document='FAC_COMPRA',
            date=datetime.now(),
            due_date=datetime.now() + timedelta(days=45),
            status='PENDIENTE',
            total_price=Decimal('900.00'),
            total_margin=Decimal('100.00')
        )

        url = reverse('customer-invoice-detail',
                      kwargs={'invoice_id': purchase_invoice.id})
        response = self.client.get(url)

        assert response.status_code == 200

        data = response.json()
        invoice_data = data['invoice']

        assert invoice_data['type_document'] == 'FAC_COMPRA'
        assert invoice_data['num_invoice'] == '200-000001'
        assert float(invoice_data['total_price']) == 900.00

    def teardown_method(self):
        """Limpieza después de cada test"""
        # Los objetos se limpian automáticamente por @pytest.mark.django_db
        pass
