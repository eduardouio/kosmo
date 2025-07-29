from trade.models import Invoice
from trade.models import Payment
from trade.models.Payment import PaymentDetail
from decimal import Decimal


class InvoiceBalance:
    @classmethod
    def get_invoice_balance(cls, invoice_id):
        """
        Calcula el saldo pendiente de una factura específica.
        """
        try:
            invoice = Invoice.objects.get(id=invoice_id, is_active=True)

            # Verificar si la factura está anulada
            if invoice.status == 'ANULADO':
                return {
                    'invoice': invoice,
                    'total_amount': invoice.total_invoice,
                    'paid_amount': Decimal('0.00'),
                    'balance': Decimal('0.00'),
                    'status': 'ANULADO'
                }

            # Obtener la suma de todos los pagos asociados a esta factura a través de PaymentDetail
            payment_details = PaymentDetail.objects.filter(
                invoice=invoice,
                payment__is_active=True,
                is_active=True
            )

            paid_amount = Decimal('0.00')
            for payment_detail in payment_details:
                paid_amount += payment_detail.amount

            balance = invoice.total_invoice - paid_amount

            # Actualizar estado si está completamente pagada
            if balance <= 0 and invoice.status != 'PAGADO':
                invoice.status = 'PAGADO'
                invoice.save()
            elif balance > 0 and invoice.status == 'PAGADO':
                invoice.status = 'PENDIENTE'
                invoice.save()

            return {
                'invoice': invoice,
                'total_amount': invoice.total_invoice,
                'paid_amount': paid_amount,
                'balance': balance,
                'status': invoice.status
            }
        except Invoice.DoesNotExist:
            return None

    @classmethod
    def get_pending_invoices(cls, partner_id=None):
        """
        Retorna todas las facturas pendientes de pago, opcionalmente filtradas por cliente.
        """
        query = Invoice.objects.filter(
            is_active=True,
            status='PENDIENTE'
        )

        if partner_id:
            query = query.filter(partner_id=partner_id)

        invoices_data = []

        for invoice in query:
            balance_data = cls.get_invoice_balance(invoice.id)
            if balance_data and balance_data['balance'] > 0:
                invoices_data.append(balance_data)

        return invoices_data

    @classmethod
    def apply_payment_to_invoices(cls, payment_id, invoice_amounts):
        """
        Aplica un pago a múltiples facturas con montos específicos para cada una.

        Args:
            payment_id (int): ID del pago
            invoice_amounts (dict): Diccionario con {invoice_id: monto_a_aplicar}
        """
        try:
            payment = Payment.objects.get(id=payment_id)
            total_applied = Decimal('0.00')

            for invoice_id, amount in invoice_amounts.items():
                amount = Decimal(str(amount))
                invoice = Invoice.objects.get(id=invoice_id)
                
                # Crear o actualizar PaymentDetail
                payment_detail, created = PaymentDetail.objects.get_or_create(
                    payment=payment,
                    invoice=invoice,
                    defaults={'amount': amount}
                )
                
                if not created:
                    payment_detail.amount = amount
                    payment_detail.save()
                
                total_applied += amount

                # Verificar si la factura ya está pagada completamente
                balance_data = cls.get_invoice_balance(invoice_id)
                if balance_data and balance_data['balance'] <= 0:
                    invoice.status = 'PAGADO'
                    invoice.save()

            return True
        except Exception as e:
            print(f"Error al aplicar pago: {str(e)}")
            return False
