from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import date, datetime, timedelta

from trade.models import Invoice
from trade.models.Payment import PaymentDetail
from partners.models import Partner


class PartnerAccountStatmentView(TemplateView):
    """Reporte de estado de cuenta de un Partner (cliente).

    Reglas:
        - Rango fechas vía GET: start_date, end_date (YYYY-MM-DD).
            Defecto: mes actual.
        - Incluir facturas (pagadas o pendientes) dentro del rango.
        - Incluir pagos del rango para facturas incluidas.
        - Sin partner_id => página informativa.
    """

    template_name = 'reports/partner_account_statment.html'

    def _parse_date(self, value, default):
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception:
            return default

    def get_context_data(self, **kwargs):  # noqa: C901 complejidad aceptable
        ctx = super().get_context_data(**kwargs)
        today = date.today()

        # Rango por defecto: mes actual
        first_day = today.replace(day=1)
        # último día del mes actual
        next_month = (
            first_day.replace(day=28) + timedelta(days=4)
        ).replace(day=1)
        last_day = next_month - timedelta(days=1)

        start_param = self.request.GET.get('start_date')
        end_param = self.request.GET.get('end_date')
        partner_id = self.request.GET.get('partner_id')

        start_date = self._parse_date(start_param, first_day)
        end_date = self._parse_date(end_param, last_day)

        ctx.update({
            'start_date': start_date,
            'end_date': end_date,
            'today': today,
        })

        if not partner_id:
            ctx['missing_partner'] = True
            return ctx

        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            ctx['partner_not_found'] = True
            return ctx

        # Solo facturas dentro del rango de fechas
        invoices = Invoice.objects.filter(
            partner=partner,
            is_active=True,
            date__date__gte=start_date,
            date__date__lte=end_date,
        ).select_related('partner').order_by('date')

        invoice_ids = list(invoices.values_list('id', flat=True))

        # Pagos del rango vinculados a facturas incluidas
        payment_details = PaymentDetail.objects.filter(
            invoice_id__in=invoice_ids,
            payment__date__gte=start_date,
            payment__date__lte=end_date,
            is_active=True,
            payment__is_active=True,
        ).select_related('payment', 'invoice').order_by(
            'payment__date', 'id'
        )

        # Indexar pagos por factura
        payments_by_invoice = {}
        for pd in payment_details:
            payments_by_invoice.setdefault(pd.invoice_id, []).append(pd)

        entries = []
        total_invoices_amount = 0
        total_payments_amount = 0
        total_pending_balance = 0
        net_balance = 0

        def _to_date(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val.date()
            return val

        for inv in invoices:
            # Total de pagos aplicados (activos) a la factura DENTRO DEL RANGO
            payments_in_range_sum = sum(
                p.amount for p in payments_by_invoice.get(inv.id, [])
            )
            
            # Para el balance, usamos todos los pagos históricos de la factura
            all_payments_sum = (
                PaymentDetail.objects.filter(
                    invoice=inv,
                    is_active=True,
                    payment__is_active=True,
                ).aggregate(s=Sum('amount'))['s'] or 0
            )
            
            # permitir negativo (saldo a favor)
            # Usar total_invoice que incluye margen para facturas de venta
            balance = (inv.total_invoice or 0) - all_payments_sum

            # Días de crédito restantes: credit_term - días transcurridos
            inv_date_only = _to_date(inv.date)
            days_passed = (today - inv_date_only).days if inv_date_only else 0
            credit_term = getattr(inv.partner, 'credit_term', 0) or 0
            credit_days = credit_term - days_passed

            # Determinar referencia
            if inv.status == 'ANULADO':
                reference = 'FACTURA ANULADA'
            elif balance == 0:
                reference = 'FACTURA PAGADA'
            elif credit_days < 0:
                reference = 'FACTURA VENCIDA'
            else:
                reference = 'FACTURA'

            entries.append({
                'type': 'INVOICE',
                'date': inv_date_only,
                'document': inv.num_invoice or f'INV-{inv.id}',
                'credit_days': credit_days,
                # Usar total_invoice para incluir margen en facturas de venta
                'invoice_amount': inv.total_invoice,
                'payment_amount': (
                    payments_in_range_sum
                    if payments_in_range_sum else None
                ),
                'balance': balance,
                'reference': reference,
                'invoice': inv,
            })

            # Usar total_invoice que incluye margen para facturas de venta
            total_invoices_amount += float(inv.total_invoice or 0)
            total_payments_amount += float(payments_in_range_sum)
            if inv.status == 'PENDIENTE' and balance > 0:
                total_pending_balance += float(balance)
            net_balance += float(balance)

            # Agregar cada pago como línea independiente (solo del rango)
            for p in payments_by_invoice.get(inv.id, []):
                entries.append({
                    'type': 'PAYMENT',
                    'date': _to_date(p.payment.date),
                    'document': (
                        p.payment.payment_number or f'PAGO-{p.payment.id}'
                    ),
                    'credit_days': '',
                    'invoice_amount': None,
                    'payment_amount': p.amount,
                    'balance': None,
                    'reference': 'PAGO RECIBIDO',
                    'payment': p.payment,
                })

        # Ordenar: fecha, luego tipo (factura antes que pago)
        entries.sort(
            key=lambda e: (
                e['date'] or date.min,
                0 if e['type'] == 'INVOICE' else 1,
            )
        )

        ctx.update({
            'partner': partner,
            'entries': entries,
            'total_invoices_amount': total_invoices_amount,
            'total_payments_amount': total_payments_amount,
            'total_pending_balance': total_pending_balance,
            'net_balance': net_balance,
        })
        return ctx
