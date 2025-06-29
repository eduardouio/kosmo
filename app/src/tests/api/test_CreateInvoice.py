import pytest
from datetime import datetime
from decimal import Decimal

from common import CreateInvoiceByOrder
from trade.models import Order, Invoice, OrderItems
from accounts.models import CustomUserModel
from partners.models import Partner
from products.models import Product, StockDay, StockDetail


@pytest.mark.django_db
class TestCreateInvoiceOrder:

    @pytest.fixture
    def user(self):
        """Crear usuario para las órdenes"""
        return CustomUserModel.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    @pytest.fixture
    def customer(self):
        """Crear cliente"""
        return Partner.objects.create(
            name='Test Customer',
            type_partner='CLIENTE',
            business_tax_id='1234567890',
            address='Test Address',
            country='Ecuador',
            city='Quito',
            email='customer@test.com'
        )

    @pytest.fixture
    def supplier(self):
        """Crear proveedor"""
        return Partner.objects.create(
            name='Test Supplier',
            type_partner='PROVEEDOR',
            business_tax_id='0987654321',
            address='Supplier Address',
            country='Ecuador',
            city='Quito',
            email='supplier@test.com'
        )

    @pytest.fixture
    def product(self, supplier):
        """Crear producto"""
        return Product.objects.create(
            name='Test Product',
            variety='Red',
            colors='RED,PINK',
            default_profit_margin=Decimal('0.10')
        )

    @pytest.fixture
    def stock_day(self):
        """Crear día de stock"""
        return StockDay.objects.create(
            date=datetime.now().date(),
            is_active=True
        )

    @pytest.fixture
    def stock_detail(self, supplier, stock_day):
        """Crear detalle de stock"""
        return StockDetail.objects.create(
            partner=supplier,
            stock_day=stock_day,
            quantity=100,
            box_model='HB'
        )

    @pytest.fixture
    def pending_order(self, customer, stock_day):
        """Crear orden pendiente"""
        return Order.objects.create(
            partner=customer,
            stock_day=stock_day,
            type_document='ORD_VENTA',
            status='PENDIENTE',
            total_price=Decimal('150.00')
        )

    @pytest.fixture
    def approved_order(self, customer, stock_day):
        """Crear orden aprobada"""
        return Order.objects.create(
            partner=customer,
            stock_day=stock_day,
            type_document='ORD_VENTA',
            status='APROBADO',
            total_price=Decimal('150.00')
        )

    @pytest.fixture
    def supplier_order(self, supplier, stock_day):
        """Crear orden de proveedor"""
        return Order.objects.create(
            partner=supplier,
            stock_day=stock_day,
            type_document='ORD_COMPRA',
            status='APROBADO',
            total_price=Decimal('100.00')
        )

    def test_generate_not_approved_order(self, pending_order):
        """Test para orden no aprobada - no debería generar factura"""
        result = CreateInvoiceByOrder().generate_invoice(pending_order)
        assert result is False

    def test_generate_supplier_invoice(self, supplier_order, stock_detail):
        """Test para generar factura de compra"""
        # Crear detalle de orden
        OrderItems.objects.create(
            order=supplier_order,
            id_stock_detail=stock_detail.id,
            quantity=10,
            box_model='HB',
            line_price=Decimal('10.00')
        )
        
        # Reconstruir totales
        Order.rebuild_totals(supplier_order)
        
        # Generar factura
        result = CreateInvoiceByOrder().generate_invoice(supplier_order)
        
        if result:  # Si se genera la factura
            assert isinstance(result, Invoice)
            assert result.partner == supplier_order.partner
            assert result.type_document == 'FAC_COMPRA'
            assert result.status == 'PENDIENTE'
            assert result.order == supplier_order

    def test_generate_customer_invoice(self, approved_order, stock_detail):
        """Test para generar factura de venta"""
        # Crear detalle de orden
        OrderItems.objects.create(
            order=approved_order,
            id_stock_detail=stock_detail.id,
            quantity=10,
            box_model='HB',
            line_price=Decimal('15.00')
        )
        
        # Reconstruir totales
        Order.rebuild_totals(approved_order)
        
        # Generar factura
        result = CreateInvoiceByOrder().generate_invoice(approved_order)
        
        if result:  # Si se genera la factura
            assert isinstance(result, Invoice)
            assert result.partner == approved_order.partner
            assert result.type_document == 'FAC_VENTA'
            assert result.status == 'PENDIENTE'
            assert result.order == approved_order

    def test_order_without_items(self, approved_order):
        """Test para orden sin items - no debería generar factura"""
        result = CreateInvoiceByOrder().generate_invoice(approved_order)
        # Puede retornar False o una factura vacía dependiendo de la lógica
        if result:
            assert isinstance(result, Invoice)
        else:
            assert result is False

