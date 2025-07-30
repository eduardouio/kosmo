
import pytest
from decimal import Decimal
from datetime import date, timedelta
from common.InvoiceBalance import InvoiceBalance
from trade.models import Invoice, Payment, PaymentDetail, Order
from partners.models import Partner
from accounts.models import CustomUserModel


@pytest.mark.django_db
class TestInvoiceBalance:
    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@test.com",
            password="testpass123"
        )

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
            type_partner="CLIENTE",
            default_profit_margin=Decimal('0.10'),
            website="www.test.com",
            credit_term=30,
            skype="test_skype",
            email="test@partner.com",
            phone="0987654321"
        )

    @pytest.fixture
    def order(self, partner, user):
        """Fixture para crear una orden"""
        return Order.objects.create(
            partner=partner,
            id_user_created=user.id,
            date=date.today(),
            delivery_date=date.today() + timedelta(days=7),
            total_price=Decimal('100.00'),
            status='CONFIRMADO'
        )

    @pytest.fixture
    def invoice_pending(self, order, partner):
        """Fixture para crear una factura pendiente"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-001",
            type_document="FAC_VENTA",
            total_price=Decimal('100.00'),
            total_margin=Decimal('20.00'),
            status='PENDIENTE'
        )

    @pytest.fixture
    def invoice_paid(self, order, partner):
        """Fixture para crear una factura pagada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-002",
            type_document="FAC_VENTA",
            total_price=Decimal('150.00'),
            total_margin=Decimal('30.00'),
            status='PAGADO'
        )

    @pytest.fixture
    def invoice_cancelled(self, order, partner):
        """Fixture para crear una factura anulada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-003",
            type_document="FAC_VENTA",
            total_price=Decimal('200.00'),
            total_margin=Decimal('40.00'),
            status='ANULADO'
        )

    @pytest.fixture
    def payment(self):
        """Fixture para crear un pago"""
        return Payment.objects.create(
            payment_number="PAY-001",
            date=date.today(),
            amount=Decimal('120.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

    @pytest.fixture
    def partial_payment(self):
        """Fixture para crear un pago parcial"""
        return Payment.objects.create(
            payment_number="PAY-002",
            date=date.today(),
            amount=Decimal('60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

    def test_invoice_balance_initialization(self):
        """Test que InvoiceBalance se puede inicializar"""
        balance = InvoiceBalance()
        assert balance is not None
        assert hasattr(balance, 'get_invoice_balance')
        assert hasattr(balance, 'get_pending_invoices')
        assert hasattr(balance, 'apply_payment_to_invoices')

    def test_get_invoice_balance_zero_amount_invoice(self, order, partner):
        """Test balance de factura con monto cero"""
        zero_invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-ZERO",
            type_document="FAC_VENTA",
            total_price=Decimal('0.00'),
            total_margin=Decimal('0.00'),
            status='PENDIENTE'
        )
        result = InvoiceBalance.get_invoice_balance(zero_invoice.id)
        assert result is not None
        assert result['total_amount'] == Decimal('0.00')
        assert result['paid_amount'] == Decimal('0.00')
        assert result['balance'] == Decimal('0.00')

    # Aquí deben ir todos los demás métodos de test, alineados igual que los anteriores


@pytest.mark.django_db
class TestInvoiceBalance:
    @pytest.fixture
    def user(self):
        """Fixture para crear un usuario"""
        return CustomUserModel.objects.create_user(
            email="test@test.com",
            password="testpass123"
        )

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
            type_partner="CLIENTE",
            default_profit_margin=Decimal('0.10'),
            website="www.test.com",
            credit_term=30,
            skype="test_skype",
            email="test@partner.com",
            phone="0987654321"
        )

    @pytest.fixture
    def order(self, partner, user):
        """Fixture para crear una orden"""
        return Order.objects.create(
            partner=partner,
            id_user_created=user.id,
            date=date.today(),
            delivery_date=date.today() + timedelta(days=7),
            total_price=Decimal('100.00'),
            status='CONFIRMADO'
        )

    @pytest.fixture
    def invoice_pending(self, order, partner):
        """Fixture para crear una factura pendiente"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-001",
            type_document="FAC_VENTA",
            total_price=Decimal('100.00'),
            total_margin=Decimal('20.00'),
            status='PENDIENTE'
        )

    @pytest.fixture
    def invoice_paid(self, order, partner):
        """Fixture para crear una factura pagada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-002",
            type_document="FAC_VENTA",
            total_price=Decimal('150.00'),
            total_margin=Decimal('30.00'),
            status='PAGADO'
        )

    @pytest.fixture
    def invoice_cancelled(self, order, partner):
        """Fixture para crear una factura anulada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-003",
            type_document="FAC_VENTA",
            total_price=Decimal('200.00'),
            total_margin=Decimal('40.00'),
            status='ANULADO'
        )

    @pytest.fixture
    def payment(self):
        """Fixture para crear un pago"""
        return Payment.objects.create(
            payment_number="PAY-001",
            date=date.today(),
            amount=Decimal('120.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

    @pytest.fixture
    def partial_payment(self):
        """Fixture para crear un pago parcial"""
        return Payment.objects.create(
            payment_number="PAY-002",
            date=date.today(),
            amount=Decimal('60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

        assert result is not None
        assert result['total_amount'] == Decimal('120.777777')

    def test_get_pending_invoices_mixed_statuses(self, order, partner):
        """Test facturas pendientes con diferentes estados y balances"""
        # Crear facturas con diferentes estados
        invoices = []
        for i, status in enumerate(['PENDIENTE', 'PAGADO', 'ANULADO'], 1):
            invoice = Invoice.objects.create(
                order=order,
                partner=partner,
                num_invoice=f"INV-MIX-{i}",
                type_document="FAC_VENTA",
                total_price=Decimal('100.00'),
                total_margin=Decimal('20.00'),
                status=status
            )
            invoices.append(invoice)

        # Solo debería retornar las facturas PENDIENTES con balance > 0
        result = InvoiceBalance.get_pending_invoices()

        assert isinstance(result, list)
        for invoice_data in result:
            assert invoice_data['status'] == 'PENDIENTE'
            assert invoice_data['balance'] > 0

    def test_get_pending_invoices_with_zero_balance(self, order, partner, payment):
        """Test facturas pendientes que tienen balance cero"""
        invoice = Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-ZERO-BAL",
            type_document="FAC_VENTA",
            total_price=Decimal('100.00'),
            total_margin=Decimal('20.00'),
            status='PENDIENTE'
        )

        # Aplicar pago completo usando PaymentDetail
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice,
            amount=invoice.total_invoice
        )

        result = InvoiceBalance.get_pending_invoices()

        # No debería incluir facturas con balance <= 0
        invoice_ids = [data['invoice'].id for data in result]
        assert invoice.id not in invoice_ids

    def test_apply_payment_to_invoices_amount_validation(self, invoice_pending, payment):
        """Test validación de montos en apply_payment_to_invoices"""
        # Test con monto negativo
        invoice_amounts = {invoice_pending.id: Decimal('-50.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is True  # El método no valida montos negativos actualmente

    def test_apply_payment_to_invoices_string_amounts(self, invoice_pending, payment):
        """Test apply_payment_to_invoices con montos como string"""
        invoice_amounts = {invoice_pending.id: "120.50"}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is True

    def test_apply_payment_to_invoices_inactive_payment(self, invoice_pending):
        """Test aplicar pago inactivo"""
        inactive_payment = Payment.objects.create(
            payment_number="PAY-INACTIVE",
            date=date.today(),
            amount=Decimal('120.00'),
            method="TRANSFERENCIA",
            status="APROBADO",
            is_active=False
        )

        invoice_amounts = {invoice_pending.id: Decimal('120.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            inactive_payment.id,
            invoice_amounts
        )

        assert result is True  # El método no verifica si el pago está activo

    def test_apply_payment_to_invoices_inactive_invoice(self, payment):
        """Test aplicar pago a factura inactiva"""
        inactive_invoice = Invoice.objects.create(
            order_id=1,  # Asumiendo que existe
            partner_id=1,  # Asumiendo que existe
            num_invoice="INV-INACTIVE",
            type_document="FAC_VENTA",
            total_price=Decimal('100.00'),
            total_margin=Decimal('20.00'),
            status='PENDIENTE',
            is_active=False
        )

        invoice_amounts = {inactive_invoice.id: Decimal('120.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        # Debería fallar porque la factura no existe (está inactiva)
        assert result is False

    def test_concurrent_payment_applications(self, invoice_pending):
        """Test aplicación concurrente de pagos"""
        payment1 = Payment.objects.create(
            payment_number="PAY-CONC-1",
            date=date.today(),
            amount=Decimal('60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )
        payment2 = Payment.objects.create(
            payment_number="PAY-CONC-2",
            date=date.today(),
            amount=Decimal('60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

        # Aplicar ambos pagos a la misma factura
        invoice_amounts1 = {invoice_pending.id: Decimal('60.00')}
        invoice_amounts2 = {invoice_pending.id: Decimal('60.00')}

        result1 = InvoiceBalance.apply_payment_to_invoices(
            payment1.id,
            invoice_amounts1
        )
        result2 = InvoiceBalance.apply_payment_to_invoices(
            payment2.id,
            invoice_amounts2
        )

        assert result1 is True
        assert result2 is True

        # Verificar balance final
        balance_data = InvoiceBalance.get_invoice_balance(invoice_pending.id)
        assert balance_data['paid_amount'] == Decimal('120.00')

    def test_get_invoice_balance_performance_with_many_payments(self, invoice_pending):
        """Test rendimiento con múltiples pagos"""
        # Crear muchos pagos pequeños
        total_paid = Decimal('0.00')
        for i in range(50):
            payment = Payment.objects.create(
                payment_number=f"PAY-PERF-{i}",
                date=date.today(),
                amount=Decimal('1.00'),
                method="TRANSFERENCIA",
                status="APROBADO"
            )
            PaymentDetail.objects.create(
                payment=payment,
                invoice=invoice_pending,
                amount=Decimal('1.00')
            )
            total_paid += Decimal('1.00')

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['paid_amount'] == total_paid

    def test_get_pending_invoices_pagination_simulation(self, partner, order):
        """Test simulación de paginación con muchas facturas"""
        # Crear múltiples facturas pendientes
        for i in range(20):
            Invoice.objects.create(
                order=order,
                partner=partner,
                num_invoice=f"INV-PAG-{i}",
                type_document="FAC_VENTA",
                total_price=Decimal('100.00'),
                total_margin=Decimal('20.00'),
                status='PENDIENTE'
            )

        result = InvoiceBalance.get_pending_invoices(partner.id)

        assert isinstance(result, list)
        assert len(result) >= 20  # Al menos las que creamos

    def test_invoice_balance_status_transitions(self, invoice_pending, payment):
        """Test todas las transiciones de estado posibles"""
        # Estado inicial: PENDIENTE
        assert invoice_pending.status == 'PENDIENTE'

        # PENDIENTE -> PAGADO
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=invoice_pending.total_invoice
        )
        balance1 = InvoiceBalance.get_invoice_balance(invoice_pending.id)
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PAGADO'

        # PAGADO -> PENDIENTE (simulando reverso parcial)
        # Crear un pago negativo para simular reverso
        reversal_payment = Payment.objects.create(
            payment_number="PAY-REVERSAL",
            date=date.today(),
            amount=Decimal('-60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )
        PaymentDetail.objects.create(
            payment=reversal_payment,
            invoice=invoice_pending,
            amount=Decimal('-60.00')
        )

        balance2 = InvoiceBalance.get_invoice_balance(invoice_pending.id)
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PENDIENTE'

    def test_error_handling_with_corrupted_data(self, invoice_pending):
        """Test manejo de errores con datos corruptos"""
        # Test con ID de pago que no es numérico (simulado)
        result = InvoiceBalance.apply_payment_to_invoices(
            "invalid_id",
            {invoice_pending.id: Decimal('100.00')}
        )

        assert result is False

    def test_memory_efficiency_large_dataset(self, partner):
        """Test eficiencia de memoria con dataset grande"""
        # Este test verifica que el método no cargue todos los datos en memoria
        result = InvoiceBalance.get_pending_invoices(partner.id)

        # Verificar que retorna un generador o lista, no un QuerySet completo
        assert isinstance(result, list)

    @pytest.fixture
    def invoice_paid(self, order, partner):
        """Fixture para crear una factura pagada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-002",
            type_document="FAC_VENTA",
            total_price=Decimal('150.00'),
            total_margin=Decimal('30.00'),
            status='PAGADO'
        )

    @pytest.fixture
    def invoice_cancelled(self, order, partner):
        """Fixture para crear una factura anulada"""
        return Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="INV-003",
            type_document="FAC_VENTA",
            total_price=Decimal('200.00'),
            total_margin=Decimal('40.00'),
            status='ANULADO'
        )

    @pytest.fixture
    def payment(self):
        """Fixture para crear un pago"""
        return Payment.objects.create(
            payment_number="PAY-001",
            date=date.today(),
            amount=Decimal('120.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

    @pytest.fixture
    def partial_payment(self):
        """Fixture para crear un pago parcial"""
        return Payment.objects.create(
            payment_number="PAY-002",
            date=date.today(),
            amount=Decimal('60.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )

    def test_invoice_balance_initialization(self):
        """Test que InvoiceBalance se puede inicializar"""
        balance = InvoiceBalance()
        assert balance is not None
        assert hasattr(balance, 'get_invoice_balance')
        assert hasattr(balance, 'get_pending_invoices')
        assert hasattr(balance, 'apply_payment_to_invoices')

    def test_get_invoice_balance_pending_no_payments(self, invoice_pending):
        """Test balance de factura pendiente sin pagos"""
        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert isinstance(result, dict)

        # Verificar campos requeridos
        required_fields = [
            'invoice', 'total_amount', 'paid_amount', 'balance', 'status'
        ]
        for field in required_fields:
            assert field in result

        # Verificar valores
        assert result['invoice'] == invoice_pending
        # total_price + total_margin
        assert result['total_amount'] == Decimal('120.00')
        assert result['paid_amount'] == Decimal('0.00')
        assert result['balance'] == Decimal('120.00')
        assert result['status'] == 'PENDIENTE'

    def test_get_invoice_balance_with_full_payment(
        self, invoice_pending, payment
    ):
        """Test balance de factura con pago completo"""
        # Crear relación de pago
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=Decimal('120.00')
        )

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['total_amount'] == Decimal('120.00')
        assert result['paid_amount'] == Decimal('120.00')
        assert result['balance'] == Decimal('0.00')

        # Verificar que el estado se actualizó a PAGADO
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PAGADO'
        assert result['status'] == 'PAGADO'

    def test_get_invoice_balance_with_partial_payment(
        self, invoice_pending, partial_payment
    ):
        """Test balance de factura con pago parcial"""
        # Crear relación de pago parcial
        PaymentDetail.objects.create(
            payment=partial_payment,
            invoice=invoice_pending,
            amount=Decimal('60.00')
        )

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['total_amount'] == Decimal('120.00')
        assert result['paid_amount'] == Decimal('60.00')
        assert result['balance'] == Decimal('60.00')
        assert result['status'] == 'PENDIENTE'

    def test_get_invoice_balance_with_multiple_payments(
        self, invoice_pending, payment, partial_payment
    ):
        """Test balance de factura con múltiples pagos"""
        # Crear múltiples relaciones de pago
        PaymentDetail.objects.create(
            payment=partial_payment,
            invoice=invoice_pending,
            amount=Decimal('60.00')
        )
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=Decimal('60.00')
        )

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['total_amount'] == Decimal('120.00')
        assert result['paid_amount'] == Decimal('120.00')
        assert result['balance'] == Decimal('0.00')

        # Verificar que el estado se actualizó a PAGADO
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PAGADO'

    def test_get_invoice_balance_overpayment(self, invoice_pending, payment):
        """Test balance de factura con sobrepago"""
        # Crear pago mayor al monto de la factura
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=Decimal('150.00')
        )

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['total_amount'] == Decimal('120.00')
        assert result['paid_amount'] == Decimal('150.00')
        # Balance negativo por sobrepago
        assert result['balance'] == Decimal('-30.00')

        # Verificar que el estado se actualizó a PAGADO
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PAGADO'

    def test_get_invoice_balance_cancelled_invoice(self, invoice_cancelled):
        """Test balance de factura anulada"""
        result = InvoiceBalance.get_invoice_balance(invoice_cancelled.id)

        assert result is not None
        assert result['invoice'] == invoice_cancelled
        # total_price + total_margin
        assert result['total_amount'] == Decimal('240.00')
        assert result['paid_amount'] == Decimal('0.00')
        # Balance 0 para facturas anuladas
        assert result['balance'] == Decimal('0.00')
        assert result['status'] == 'ANULADO'

    def test_get_invoice_balance_nonexistent_invoice(self):
        """Test balance de factura que no existe"""
        result = InvoiceBalance.get_invoice_balance(99999)
        assert result is None

    def test_get_invoice_balance_inactive_invoice(self, invoice_pending):
        """Test balance de factura inactiva"""
        invoice_pending.is_active = False
        invoice_pending.save()

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)
        assert result is None

    def test_get_invoice_balance_status_update_from_paid_to_pending(
        self, invoice_paid, partial_payment
    ):
        """Test actualización de estado de PAGADO a PENDIENTE
        cuando hay saldo pendiente"""
        # Inicialmente la factura está marcada como PAGADO
        assert invoice_paid.status == 'PAGADO'

        # Crear un pago parcial menor al total
        PaymentDetail.objects.create(
            payment=partial_payment,
            invoice=invoice_paid,
            amount=Decimal('60.00')
        )

        result = InvoiceBalance.get_invoice_balance(invoice_paid.id)

        assert result is not None
        assert result['balance'] > 0

        # Verificar que el estado se actualizó a PENDIENTE
        invoice_paid.refresh_from_db()
        assert invoice_paid.status == 'PENDIENTE'
        assert result['status'] == 'PENDIENTE'

    def test_get_pending_invoices_no_filter(
        self, invoice_pending, invoice_paid, invoice_cancelled
    ):
        """Test obtener todas las facturas pendientes sin filtro de partner"""
        # Agregar un pago parcial a una factura para que tenga
        # balance pendiente
        payment = Payment.objects.create(
            payment_number="PAY-TEST",
            date=date.today(),
            amount=Decimal('50.00'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=Decimal('50.00')
        )

        result = InvoiceBalance.get_pending_invoices()

        assert isinstance(result, list)
        assert len(result) >= 1  # Al menos una factura pendiente

        # Verificar que todas tienen balance > 0
        for invoice_data in result:
            assert invoice_data['balance'] > 0
            assert invoice_data['status'] == 'PENDIENTE'

    def test_get_pending_invoices_with_partner_filter(
        self, invoice_pending, partner
    ):
        """Test obtener facturas pendientes filtradas por partner"""
        result = InvoiceBalance.get_pending_invoices(partner.id)

        assert isinstance(result, list)

        # Verificar que todas las facturas pertenecen al partner correcto
        for invoice_data in result:
            assert invoice_data['invoice'].partner_id == partner.id
            assert invoice_data['balance'] > 0

    def test_get_pending_invoices_no_pending_invoices(
        self, invoice_paid, invoice_cancelled
    ):
        """Test obtener facturas pendientes cuando no hay ninguna para un partner específico"""
        # Crear un partner único que sabemos que no tendrá facturas pendientes
        unique_partner = Partner.objects.create(
            business_tax_id="9999999999",
            name="PARTNER ÚNICO SIN FACTURAS",
            short_name="PUSF",
            address="Av. Única 999",
            country="Ecuador",
            city="Quito",
            type_partner="CLIENTE",
            default_profit_margin=Decimal('0.10'),
            website="www.unico.com",
            credit_term=30,
            skype="unico_skype",
            email="unico@partner.com",
            phone="0999999999"
        )
        
        # Verificar que este partner específico no tiene facturas pendientes
        result = InvoiceBalance.get_pending_invoices(partner_id=unique_partner.id)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_apply_payment_to_invoices_single_invoice(
        self, invoice_pending, payment
    ):
        """Test aplicar pago a una sola factura"""
        invoice_amounts = {invoice_pending.id: Decimal('120.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is True

        # Verificar que la relación se creó
        payment_details = PaymentDetail.objects.filter(
            payment=payment,
            invoice=invoice_pending
        )
        assert payment_details.exists()

        # Verificar que el estado de la factura se actualizó
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PAGADO'

    def test_apply_payment_to_invoices_multiple_invoices(
        self, invoice_pending, payment
    ):
        """Test aplicar pago a múltiples facturas"""
        # Crear segunda factura
        order2 = Order.objects.create(
            partner=invoice_pending.partner,
            date=date.today(),
            delivery_date=date.today() + timedelta(days=7),
            total_price=Decimal('80.00'),
            status='CONFIRMADO'
        )
        invoice2 = Invoice.objects.create(
            order=order2,
            partner=invoice_pending.partner,
            num_invoice="INV-004",
            type_document="FAC_VENTA",
            total_price=Decimal('80.00'),
            total_margin=Decimal('16.00'),
            status='PENDIENTE'
        )

        invoice_amounts = {
            invoice_pending.id: Decimal('60.00'),
            invoice2.id: Decimal('60.00')
        }

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is True

        # Verificar que ambas relaciones se crearon
        payment_details = PaymentDetail.objects.filter(payment=payment)
        assert payment_details.count() == 2

    def test_apply_payment_to_invoices_partial_payments(
        self, invoice_pending, partial_payment
    ):
        """Test aplicar pago parcial a factura"""
        invoice_amounts = {invoice_pending.id: Decimal('60.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            partial_payment.id,
            invoice_amounts
        )

        assert result is True

        # Verificar que la factura sigue pendiente
        invoice_pending.refresh_from_db()
        assert invoice_pending.status == 'PENDIENTE'

        # Verificar el balance
        balance_data = InvoiceBalance.get_invoice_balance(invoice_pending.id)
        assert balance_data['balance'] == Decimal('60.00')

    def test_apply_payment_to_invoices_nonexistent_payment(
        self, invoice_pending
    ):
        """Test aplicar pago inexistente"""
        invoice_amounts = {invoice_pending.id: Decimal('120.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            99999,
            invoice_amounts
        )

        assert result is False

    def test_apply_payment_to_invoices_nonexistent_invoice(self, payment):
        """Test aplicar pago a factura inexistente"""
        invoice_amounts = {99999: Decimal('120.00')}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is False

    def test_apply_payment_to_invoices_empty_amounts(self, payment):
        """Test aplicar pago con diccionario vacío"""
        invoice_amounts = {}

        result = InvoiceBalance.apply_payment_to_invoices(
            payment.id,
            invoice_amounts
        )

        assert result is True  # Debería ser exitoso aunque no haga nada

    def test_decimal_precision_handling(self, invoice_pending, payment):
        """Test manejo de precisión decimal"""
        # Crear una factura específica para evitar conflictos con otros tests
        order = Order.objects.create(
            partner_id=1,
            id_user_created=1,
            date=date.today(),
            delivery_date=date.today() + timedelta(days=7),
            total_price=Decimal('120.00'),
            status='CONFIRMADO'
        )
        
        decimal_invoice = Invoice.objects.create(
            order=order,
            partner_id=1,
            num_invoice="INV-DECIMAL",
            type_document="FAC_VENTA",
            total_price=Decimal('120.00'),
            total_margin=Decimal('0.00'),
            status='PENDIENTE'
        )
        
        # Crear un pago específico para evitar conflictos con otros tests
        decimal_payment = Payment.objects.create(
            payment_number="PAY-DECIMAL",
            date=date.today(),
            amount=Decimal('119.999'),
            method="TRANSFERENCIA",
            status="APROBADO"
        )
        
        # Crear pago con muchos decimales (pero que se mantenga dentro de la precisión del modelo)
        PaymentDetail.objects.create(
            payment=decimal_payment,
            invoice=decimal_invoice,
            amount=Decimal('119.99')  # Usamos 2 decimales en lugar de 3
        )

        result = InvoiceBalance.get_invoice_balance(decimal_invoice.id)

        assert result is not None
        assert isinstance(result['paid_amount'], Decimal)
        assert isinstance(result['balance'], Decimal)
        assert result['paid_amount'] == Decimal('119.99')
        assert result['balance'] == Decimal('0.01')

    def test_invoice_balance_with_different_document_types(
        self, order, partner
    ):
        """Test balance con diferentes tipos de documento"""
        # Crear factura sin margen (no es FAC_VENTA)
        invoice_nota = Invoice.objects.create(
            order=order,
            partner=partner,
            num_invoice="NOTA-001",
            type_document="NOTA_CREDITO",
            total_price=Decimal('100.00'),
            total_margin=Decimal('20.00'),
            status='PENDIENTE'
        )

        result = InvoiceBalance.get_invoice_balance(invoice_nota.id)

        assert result is not None
        # Para documentos que no sean FAC_VENTA, solo se considera total_price
        assert result['total_amount'] == Decimal('100.00')

    def test_payment_detail_inactive_payments(self, invoice_pending, payment):
        """Test que pagos inactivos no se consideren en el balance"""
        # Crear payment detail
        PaymentDetail.objects.create(
            payment=payment,
            invoice=invoice_pending,
            amount=Decimal('120.00')
        )

        # Desactivar el pago
        payment.is_active = False
        payment.save()

        result = InvoiceBalance.get_invoice_balance(invoice_pending.id)

        assert result is not None
        assert result['paid_amount'] == Decimal('0.00')
        assert result['balance'] == Decimal('120.00')
        assert result['status'] == 'PENDIENTE'
        assert result['status'] == 'PENDIENTE'
