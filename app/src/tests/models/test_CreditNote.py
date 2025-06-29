import pytest
from datetime import date
from decimal import Decimal
from trade.models import CreditNote, Invoice, Order
from partners.models import Partner
from products.models import StockDay


@pytest.mark.django_db
class TestCreditNote:

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

    def test_create_credit_note(self, invoice):
        """Test creación de nota de crédito"""
        credit_note = CreditNote.objects.create(
            num_credit_note="nc-001",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("150.00"),
            reason="producto defectuoso"
        )
        assert credit_note.num_credit_note == "NC-001"
        assert credit_note.invoice == invoice
        assert credit_note.date == date(2024, 1, 20)
        assert credit_note.amount == Decimal("150.00")
        assert credit_note.reason == "PRODUCTO DEFECTUOSO"

    def test_uppercase_conversion(self, invoice):
        """Test conversión a mayúsculas en save"""
        credit_note = CreditNote.objects.create(
            num_credit_note="nc-002",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("200.00"),
            reason="descuento por volumen"
        )
        assert credit_note.num_credit_note == "NC-002"
        assert credit_note.reason == "DESCUENTO POR VOLUMEN"

    def test_str_method(self, invoice):
        """Test método __str__"""
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-003",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("300.00"),
            reason="Devolución de mercancía"
        )
        # El método __str__ concatena str(invoice) + ' ' + str(amount)
        expected_str = f"{str(invoice)} {str(credit_note.amount)}"
        assert str(credit_note) == expected_str

    def test_foreign_key_cascade(self, invoice):
        """Test cascade al eliminar invoice"""
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-004",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("100.00"),
            reason="Nota de crédito de prueba"
        )

        credit_note_id = credit_note.id

        # Eliminar invoice debería eliminar credit_note por CASCADE
        Invoice.objects.filter(id=invoice.id).delete()

        with pytest.raises(CreditNote.DoesNotExist):
            CreditNote.objects.get(id=credit_note_id)

    def test_decimal_field_precision(self, invoice):
        """Test precisión del campo amount"""
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-005",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("123.456"),  # Se mantiene con 3 decimales
            reason="Test precisión"
        )
        # Django mantiene precisión exacta del decimal
        assert credit_note.amount == Decimal("123.456")

    def test_date_field(self, invoice):
        """Test campo de fecha"""
        test_date = date(2024, 6, 15)
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-006",
            invoice=invoice,
            date=test_date,
            amount=Decimal("50.00"),
            reason="Test fecha"
        )
        assert credit_note.date == test_date
        assert isinstance(credit_note.date, date)

    def test_text_field_reason(self, invoice):
        """Test campo TextField reason"""
        long_reason = "Esta es una razón muy larga para la nota " * 10
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-007",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("75.00"),
            reason=long_reason
        )
        assert credit_note.reason == long_reason.upper()

    def test_auto_field_id(self, invoice):
        """Test que el ID es auto generado"""
        credit_note = CreditNote.objects.create(
            num_credit_note="NC-008",
            invoice=invoice,
            date=date(2024, 1, 20),
            amount=Decimal("25.00"),
            reason="Test ID"
        )
        assert credit_note.id is not None
        assert isinstance(credit_note.id, int)
        assert credit_note.id > 0
