import pytest
from datetime import date
from decimal import Decimal
from django.core.exceptions import ValidationError
from trade.models import Payment, PaymentDetail, Invoice, Order
from partners.models import Partner
from products.models import StockDay
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestPayment:
    
    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@example.com",
            password="testpass123"
        )
    
    @pytest.fixture
    def partner(self):
        """Fixture para crear un partner"""
        return Partner.objects.create(
            business_tax_id="1234567890",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )
        
    @pytest.fixture
    def stock_day(self):
        """Fixture para crear un stock day"""
        return StockDay.objects.create(date=date(2024, 1, 15))
        
    @pytest.fixture
    def order(self, partner, stock_day):
        """Fixture para crear una orden"""
        return Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CONFIRMADO"
        )
        
    @pytest.fixture
    def invoice(self, order, partner):
        """Fixture para crear una factura"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            total_price=Decimal("1000.00")
        )
        
    def test_create_payment(self, user):
        """Test creación de pago"""
        payment = Payment.objects.create(
            payment_number="PAG-001",
            date=date(2024, 1, 20),
            amount=Decimal("500.00"),
            method="TRANSF",
            bank="banco pichincha",
            nro_account="1234567890",
            nro_operation="op123456",
            processed_by=user
        )
        assert payment.payment_number == "PAG-001"
        assert payment.date == date(2024, 1, 20)
        assert payment.amount == Decimal("500.00")
        assert payment.method == "TRANSF"
        assert payment.bank == "BANCO PICHINCHA"
        assert payment.nro_account == "1234567890"
        assert payment.nro_operation == "OP123456"
        assert payment.processed_by == user
        
    def test_method_choices(self):
        """Test choices de método de pago"""
        methods = ['TRANSF', 'CHEQUE', 'EFECTIVO', 'OTRO', 'TC', 'TD', 'NC']
        
        for method in methods:
            payment = Payment.objects.create(
                date=date(2024, 1, 20),
                amount=Decimal("100.00"),
                method=method
            )
            assert payment.method == method
            
    def test_type_transaction_choices(self):
        """Test choices de tipo de transacción"""
        # Ingreso (default)
        payment_income = Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("500.00"),
            type_transaction="INGRESO"
        )
        assert payment_income.type_transaction == "INGRESO"
        
        # Egreso
        payment_expense = Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("300.00"),
            type_transaction="EGRESO"
        )
        assert payment_expense.type_transaction == "EGRESO"
        
    def test_status_choices(self):
        """Test choices de status"""
        status_options = ['PENDIENTE', 'CONFIRMADO', 'RECHAZADO', 'ANULADO']
        
        for status in status_options:
            payment = Payment.objects.create(
                date=date(2024, 1, 20),
                amount=Decimal("100.00"),
                status=status
            )
            assert payment.status == status
            
    def test_default_values(self):
        """Test valores por defecto"""
        payment = Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("100.00")
        )
        assert payment.type_transaction == "INGRESO"
        assert payment.method == "OTRO"
        assert payment.status == "PENDIENTE"
        
    def test_uppercase_conversion(self):
        """Test conversión a mayúsculas en save"""
        payment = Payment.objects.create(
            payment_number="pag-002",
            date=date(2024, 1, 20),
            amount=Decimal("200.00"),
            bank="banco del pacífico",
            nro_account="acc123456",
            nro_operation="op789012"
        )
        assert payment.payment_number == "PAG-002"
        assert payment.bank == "BANCO DEL PACÍFICO"
        assert payment.nro_account == "ACC123456"
        assert payment.nro_operation == "OP789012"
        
    def test_unique_payment_number(self):
        """Test restricción unique del payment_number"""
        Payment.objects.create(
            payment_number="PAG-UNIQUE",
            date=date(2024, 1, 20),
            amount=Decimal("100.00")
        )
        
        with pytest.raises(Exception):  # IntegrityError por unique constraint
            Payment.objects.create(
                payment_number="PAG-UNIQUE",
                date=date(2024, 1, 21),
                amount=Decimal("200.00")
            )
            
    def test_clean_validation_positive_amount(self):
        """Test validación de monto positivo"""
        payment = Payment(
            date=date(2024, 1, 20),
            amount=Decimal("-100.00")  # Monto negativo
        )
        
        with pytest.raises(ValidationError):
            payment.clean()
            
    def test_clean_validation_due_date(self):
        """Test validación de fecha de vencimiento"""
        payment = Payment(
            date=date(2024, 1, 20),
            due_date=date(2024, 1, 15),  # Fecha anterior a la de pago
            amount=Decimal("100.00")
        )
        
        with pytest.raises(ValidationError):
            payment.clean()
            
    def test_optional_fields(self):
        """Test campos opcionales"""
        payment = Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("100.00")
        )
        assert payment.payment_number is None
        assert payment.due_date is None
        assert payment.bank is None
        assert payment.nro_account is None
        assert payment.nro_operation is None
        assert not payment.document  # ImageField vacío se evalúa como False
        assert payment.processed_by is None
        assert payment.approved_by is None
        assert payment.approval_date is None
        
    def test_str_method(self):
        """Test método __str__"""
        # Con payment_number
        payment_with_number = Payment.objects.create(
            payment_number="PAG-001",
            date=date(2024, 1, 20),
            amount=Decimal("500.00")
        )
        assert str(payment_with_number) == "Pago PAG-001 - 500.00"
        
        # Sin payment_number
        payment_without_number = Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("300.00")
        )
        expected_str = f"Pago {payment_without_number.id} - 300.00"
        assert str(payment_without_number) == expected_str


@pytest.mark.django_db
class TestPaymentDetail:
    
    @pytest.fixture
    def payment(self):
        """Fixture para crear un pago"""
        return Payment.objects.create(
            date=date(2024, 1, 20),
            amount=Decimal("1000.00")
        )
    
    @pytest.fixture
    def invoice(self):
        """Fixture para crear una factura"""
        partner = Partner.objects.create(
            business_tax_id="1234567890",
            name="TEST PARTNER",
            address="Av. Test 123",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE"
        )
        stock_day = StockDay.objects.create(date=date(2024, 1, 15))
        order = Order.objects.create(
            partner=partner,
            stock_day=stock_day,
            type_document="ORD_VENTA",
            status="CONFIRMADO"
        )
        return Invoice.objects.create(
            order=order,
            partner=partner,
            type_document="FAC_VENTA",
            total_price=Decimal("500.00")
        )
        
    def test_create_payment_detail(self, payment, invoice):
        """Test creación de detalle de pago"""
        payment_detail = PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice,
            amount=Decimal("250.00")
        )
        assert payment_detail.payment == payment
        assert payment_detail.invoice == invoice
        assert payment_detail.amount == Decimal("250.00")
        
    def test_unique_together_constraint(self, payment, invoice):
        """Test restricción unique_together de payment e invoice"""
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice,
            amount=Decimal("250.00")
        )
        
        with pytest.raises(Exception):  # IntegrityError por unique constraint
            PaymentDetail.objects.create(
                payment=payment,
                invoice=invoice,
                amount=Decimal("300.00")
            )
            
    def test_clean_validation_positive_amount(self, payment, invoice):
        """Test validación de monto positivo"""
        payment_detail = PaymentDetail(
            payment=payment,
            invoice=invoice,
            amount=Decimal("-50.00")  # Monto negativo
        )
        
        with pytest.raises(ValidationError):
            payment_detail.clean()
            
    def test_foreign_key_cascade(self, payment, invoice):
        """Test cascade al eliminar payment o invoice"""
        payment_detail = PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice,
            amount=Decimal("250.00")
        )
        
        payment_detail_id = payment_detail.id
        
        # Eliminar payment debería eliminar payment_detail por CASCADE
        Payment.objects.filter(id=payment.id).delete()
        
        with pytest.raises(PaymentDetail.DoesNotExist):
            PaymentDetail.objects.get(id=payment_detail_id)
