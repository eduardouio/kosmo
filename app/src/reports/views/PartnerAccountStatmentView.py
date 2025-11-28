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

    template_name = "reports/partner_account_statment.html"

    def _parse_date(self, value, default):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return default

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()

        first_day = today.replace(day=1)

        next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = next_month - timedelta(days=1)

        start_param = self.request.GET.get("start_date")
        end_param = self.request.GET.get("end_date")
        partner_id = self.request.GET.get("partner_id")

        start_date = self._parse_date(start_param, first_day)
        end_date = self._parse_date(end_param, last_day)

        ctx.update(
            {
                "start_date": start_date,
                "end_date": end_date,
                "today": today,
            }
        )

        if not partner_id:
            ctx["missing_partner"] = True
            return ctx

        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            ctx["partner_not_found"] = True
            return ctx

        invoices = (
            Invoice.objects.filter(
                partner=partner,
                is_active=True,
                status__in=["PENDIENTE", "PAGADO"],
                date__date__gte=start_date,
                date__date__lte=end_date,
            )
            .select_related("partner")
            .order_by("date")
        )

        invoice_ids = list(invoices.values_list("id", flat=True))

        payment_details = (
            PaymentDetail.objects.filter(
                invoice_id__in=invoice_ids,
                is_active=True,
                payment__is_active=True,
            )
            .select_related("payment", "invoice")
            .order_by("payment__date", "id")
        )

        payments_by_invoice = {}
        for pd in payment_details:
            payments_by_invoice.setdefault(pd.invoice_id, []).append(pd)

        entries = []
        total_overdue_amount = 0
        invoice_count = 0

        def _to_date(val):
            if not val:
                return None
            if isinstance(val, datetime):
                return val.date()
            return val

        for inv in invoices:
            invoice_count += 1

            payments_in_range_sum = sum(
                p.amount for p in payments_by_invoice.get(inv.id, [])
            )

            # Obtener detalles de pagos para esta factura
            invoice_payments = payments_by_invoice.get(inv.id, [])
            payment_details_list = []
            for idx, pd in enumerate(invoice_payments, start=1):
                payment_details_list.append(
                    {
                        "payment_number": idx,
                        "payment_date": pd.payment.date,
                        "payment_ref": pd.payment.payment_number or f"PAY-{pd.payment.id}",
                        "payment_amount": pd.amount,
                        "payment_id": pd.payment.id,
                        "type_transaction": pd.payment.type_transaction,
                    }
                )

            all_payments_sum = (
                PaymentDetail.objects.filter(
                    invoice=inv,
                    is_active=True,
                    payment__is_active=True,
                ).aggregate(s=Sum("amount"))["s"]
                or 0
            )

            balance = (inv.total_invoice or 0) - all_payments_sum

            inv_date_only = _to_date(inv.date)
            days_passed = (today - inv_date_only).days if inv_date_only else 0
            credit_term = getattr(inv.partner, "credit_term", 0) or 0
            credit_days = credit_term - days_passed

            if inv.status == "ANULADO":
                reference = "FACTURA ANULADA"
            elif balance == 0:
                reference = "FACTURA PAGADA"
            elif credit_days < 0:
                reference = "FACTURA VENCIDA"

                if balance > 0:
                    total_overdue_amount += float(balance)
            else:
                reference = "FACTURA"

            entries.append(
                {
                    "type": "INVOICE",
                    "date": inv_date_only,
                    "document": inv.num_invoice or f"INV-{inv.id}",
                    "order_id": inv.order.id if inv.order else None,
                    "credit_days": credit_days,
                    "invoice_amount": inv.total_invoice,
                    "payment_amount": (
                        payments_in_range_sum if payments_in_range_sum else 0.00
                    ),
                    "balance": balance,
                    "reference": reference,
                    "invoice": inv,
                    "payment_details": payment_details_list,
                }
            )

        entries.sort(
            key=lambda e: (
                e["date"] or date.min,
                0 if e["type"] == "INVOICE" else 1,
            )
        )

        total_invoices_amount = 0
        total_payments_amount = 0
        total_pending_balance = 0
        net_balance = 0

        for entry in entries:
            total_invoices_amount += float(entry["invoice_amount"] or 0)
            total_payments_amount += float(entry["payment_amount"] or 0)
            total_pending_balance += float(entry["balance"] or 0)
            net_balance += float(entry["balance"] or 0)

        ctx.update(
            {
                "partner": partner,
                "entries": entries,
                "total_invoices_amount": total_invoices_amount,
                "total_payments_amount": total_payments_amount,
                "total_pending_balance": total_pending_balance,
                "net_balance": net_balance,
                "invoice_count": invoice_count,
                "total_overdue_amount": total_overdue_amount,
            }
        )
        return ctx
