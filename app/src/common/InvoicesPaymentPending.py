from django.db.models import Sum
from trade.models.Invoice import Invoice
from trade.models.Payment import Payment


class InvoicesPaymentPending:
    """
    Clase para obtener facturas pendientes de pago con sus saldos
    """

    def __init__(self, type_document=None):
        """
        Inicializa la clase con el tipo de documento a filtrar
        type_document: 'FAC_VENTA' o 'FAC_COMPRA'
        """
        self.type_document = type_document

    def get_pending_invoices_with_balances(self):
        """
        Obtiene todas las facturas pendientes con sus saldos adeudados
        considerando pagos parciales
        """
        # Filtros base
        filters = {
            'status': 'PENDIENTE',
            'is_active': True
        }

        # Agregar filtro por tipo de documento si se especifica
        if self.type_document:
            filters['type_document'] = self.type_document

        pending_invoices = Invoice.objects.filter(
            **filters
        ).select_related('partner', 'order')

        invoices_data = []

        for invoice in pending_invoices:
            # Calcular total de pagos realizados para esta factura
            total_payments = Payment.objects.filter(
                invoices=invoice,
                status='CONFIRMADO',
                is_active=True
            ).aggregate(total=Sum('amount'))['total'] or 0

            # Calcular saldo adeudado
            invoice_total = invoice.total_invoice
            balance_due = invoice_total - total_payments

            # Solo incluir si hay saldo pendiente
            if balance_due > 0:
                invoice_data = {
                    'invoice_id': invoice.id,
                    'invoice_number': invoice.num_invoice,
                    'serie': invoice.serie,
                    'consecutive': invoice.consecutive,
                    'type_document': invoice.type_document,
                    'date': invoice.date.isoformat() if invoice.date else None,
                    'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                    'partner_id': invoice.partner.id,
                    'partner_name': invoice.partner.name,
                    'partner_email': invoice.partner.email,
                    'partner_phone': invoice.partner.phone,
                    'partner_type': invoice.partner.type_partner,
                    'partner_credit_term': invoice.partner.credit_term,
                    'partner_business_tax_id': invoice.partner.business_tax_id,
                    'partner_address': invoice.partner.address,
                    'partner_city': invoice.partner.city,
                    'partner_country': invoice.partner.country,
                    'total_invoice': float(invoice_total),
                    'total_payments': float(total_payments),
                    'balance_due': float(balance_due),
                    'is_overdue': invoice.is_dued,
                    'days_overdue': invoice.days_overdue if invoice.is_dued else 0,
                    'order_id': invoice.order.id if invoice.order else None,
                    'total_price': float(invoice.total_price),
                    'total_margin': float(invoice.total_margin),
                    'qb_total': invoice.qb_total,
                    'hb_total': invoice.hb_total,
                    'fb_total': float(invoice.fb_total) if invoice.fb_total else 0,
                    'tot_stem_flower': invoice.tot_stem_flower,
                    'total_bunches': invoice.total_bunches,
                }
                invoices_data.append(invoice_data)

        return invoices_data

    def get_customer_pending_invoices(self, partner_id):
        """
        Obtiene facturas pendientes específicas de un cliente/proveedor
        """
        all_pending = self.get_pending_invoices_with_balances()
        return [inv for inv in all_pending if inv['partner_id'] == partner_id]

    def get_overdue_invoices(self):
        """
        Obtiene solo las facturas vencidas
        """
        all_pending = self.get_pending_invoices_with_balances()
        return [inv for inv in all_pending if inv['is_overdue']]


# Funciones de conveniencia para crear instancias específicas
def get_sales_pending_invoices():
    """Obtiene facturas de venta pendientes (por cobrar)"""
    instance = InvoicesPaymentPending(type_document='FAC_VENTA')
    return instance.get_pending_invoices_with_balances()


def get_purchase_pending_invoices():
    """Obtiene facturas de compra pendientes (por pagar)"""
    instance = InvoicesPaymentPending(type_document='FAC_COMPRA')
    return instance.get_pending_invoices_with_balances()


def get_all_pending_invoices():
    """Obtiene todas las facturas pendientes"""
    instance = InvoicesPaymentPending()
    return instance.get_pending_invoices_with_balances()
