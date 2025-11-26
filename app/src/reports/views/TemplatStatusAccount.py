from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import date, datetime, timedelta

from trade.models import Invoice
from trade.models.Payment import PaymentDetail
from partners.models import Partner
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event


class TemplatStatusAccount(TemplateView):
    template_name = "reports/status_account.html"

    def _parse_date(self, value, default):
        """Parsea una fecha desde string o retorna valor por defecto"""
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except Exception:
            return default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        partner_id = kwargs.get("partner_id")
        today = date.today()

        first_day = today.replace(day=1)
        next_month = (first_day.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_day = next_month - timedelta(days=1)

        start_param = self.request.GET.get("start_date")
        end_param = self.request.GET.get("end_date")

        start_date = self._parse_date(start_param, first_day)
        end_date = self._parse_date(end_param, last_day)

        context.update(
            {
                "start_date": start_date,
                "end_date": end_date,
                "today": today,
            }
        )

        if not partner_id:
            context["partner"] = None
            return context

        try:
            partner = Partner.objects.get(id=partner_id)
            context["partner"] = partner
        except Partner.DoesNotExist:
            loggin_event(f"Partner con ID {partner_id} no encontrado", error=True)
            context["partner"] = None
            return context

        invoices = (
            Invoice.objects.filter(
                partner=partner,
                is_active=True,
                status__in=["PENDIENTE", "PAGADO"],
                date__date__gte=start_date,
                date__date__lte=end_date,
            )
            .select_related("partner")
            .order_by("-date", "-id")
        )

        invoice_ids = set(invoices.values_list("id", flat=True))

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
        total_invoices_amount = 0
        total_payments_amount = 0
        total_pending_balance = 0
        net_balance = 0
        total_overdue_amount = 0
        invoice_count = 0

        def _to_date(val):
            """Convierte valor a date"""
            if not val:
                return None
            if isinstance(val, datetime):
                return val.date()
            return val

        for inv in invoices:
            invoice_count += 1

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

            invoice_payments = payments_by_invoice.get(inv.id, [])
            payments_amount = sum(p.amount for p in invoice_payments)

            entries.append(
                {
                    "type": "INVOICE",
                    "date": inv_date_only,
                    "document": inv.num_invoice or f"INV-{inv.id}",
                    "credit_days": credit_days,
                    "invoice_amount": inv.total_invoice,
                    "payment_amount": payments_amount if payments_amount else None,
                    "balance": balance,
                    "reference": reference,
                    "invoice": inv,
                }
            )

            total_invoices_amount += float(inv.total_invoice or 0)
            total_payments_amount += float(payments_amount)
            if inv.status == "PENDIENTE" and balance > 0:
                total_pending_balance += float(balance)
            net_balance += float(balance)

        def _is_numeric_start(doc_number):
            """Determina si el número de documento comienza con un número"""
            if not doc_number:
                return True
            return doc_number[0].isdigit()

        def _get_doc_prefix(doc_number):
            """Obtiene el prefijo del documento para ordenamiento"""
            if not doc_number:
                return ""
            if doc_number.startswith("SINFACT"):
                return "2_SINFACT"
            elif doc_number.startswith("SRI"):
                return "1_SRI"
            elif doc_number.startswith("MANUAL"):
                return "3_MANUAL"
            return "0_" + doc_number

        entries.sort(
            key=lambda e: (
                _get_doc_prefix(e.get("document", "")),
                -(e["date"] or date.min).toordinal(),
                e.get("document", ""),
                0 if e["type"] == "INVOICE" else 1,
            )
        )

        try:
            user_id = (
                getattr(self.request.user, "id", 1)
                if hasattr(self.request, "user")
                else 1
            )
            user_owner = CustomUserModel.get_by_id(user_id)
            context["user_owner"] = user_owner
        except Exception as e:
            loggin_event(
                f"Error al obtener usuario para el reporte: {str(e)}", error=True
            )
            context["user_owner"] = None

        context.update(
            {
                "entries": entries,
                "total_invoices_amount": total_invoices_amount,
                "total_payments_amount": total_payments_amount,
                "total_pending_balance": total_pending_balance,
                "net_balance": net_balance,
                "invoice_count": invoice_count,
                "total_overdue_amount": total_overdue_amount,
            }
        )

        return context
