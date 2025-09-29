from django.views.generic import TemplateView
from django.db.models import Sum, Q
from datetime import date, datetime, timedelta

from trade.models import Invoice
from trade.models.Payment import PaymentDetail
from partners.models import Partner


class GeneralPartnerStatmentAccount(TemplateView):
    """Reporte de estado de cuenta general para Partners.

    Funcionalidades:
        - Filtro por tipo: CLIENTES o PROVEEDORES (por defecto CLIENTES)
        - Rango fechas vía GET: start_date, end_date (YYYY-MM-DD)
        - Vista consolidada por tipo de partner únicamente
    """

    template_name = 'reports/general_partner_statment_account.html'

    def _parse_date(self, value, default):
        """Parsea una fecha en formato YYYY-MM-DD"""
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception:
            return default

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()

        # Rango por defecto: mes actual
        first_day = today.replace(day=1)
        next_month = (
            first_day.replace(day=28) + timedelta(days=4)
        ).replace(day=1)
        last_day = next_month - timedelta(days=1)

        start_param = self.request.GET.get('start_date')
        end_param = self.request.GET.get('end_date')
        partner_type = self.request.GET.get('partner_type', 'CLIENTE')  # Por defecto CLIENTES

        start_date = self._parse_date(start_param, first_day)
        end_date = self._parse_date(end_param, last_day)

        ctx.update({
            'start_date': start_date,
            'end_date': end_date,
            'today': today,
            'partner_type': partner_type,
        })

        # Solo mostrar vista consolidada por tipo
        return self._get_consolidated_account(ctx, partner_type, start_date, end_date)

    def _get_consolidated_account(self, ctx, partner_type, start_date, end_date):
        """Vista consolidada por tipo de partner"""
        
        # Obtener partners del tipo seleccionado
        partners = Partner.objects.filter(
            type_partner=partner_type,
            is_active=True
        ).order_by('name')

        # Obtener facturas del período para este tipo de partner
        invoices = Invoice.objects.filter(
            partner__type_partner=partner_type,
            partner__is_active=True,
            is_active=True,
            date__date__gte=start_date,
            date__date__lte=end_date,
        ).select_related('partner').order_by('partner__name', 'date')

        # Agrupar por partner
        partners_data = {}
        total_global_invoices = 0
        total_global_payments = 0
        total_global_balance = 0

        for invoice in invoices:
            partner_id = invoice.partner.id
            if partner_id not in partners_data:
                partners_data[partner_id] = {
                    'partner': invoice.partner,
                    'total_invoices': 0,
                    'total_payments': 0,
                    'total_balance': 0,
                    'invoice_count': 0,
                    'overdue_count': 0,
                }

            # Calcular totales del partner
            invoice_total = invoice.total_invoice or 0
            
            # Obtener pagos totales históricos de esta factura
            all_payments_sum = (
                PaymentDetail.objects.filter(
                    invoice=invoice,
                    is_active=True,
                    payment__is_active=True,
                ).aggregate(s=Sum('amount'))['s'] or 0
            )
            
            balance = invoice_total - all_payments_sum
            
            partners_data[partner_id]['total_invoices'] += float(invoice_total)
            partners_data[partner_id]['total_payments'] += float(all_payments_sum)
            partners_data[partner_id]['total_balance'] += float(balance)
            partners_data[partner_id]['invoice_count'] += 1
            
            # Verificar si está vencida
            if invoice.due_date and invoice.due_date.date() < datetime.now().date() and balance > 0:
                partners_data[partner_id]['overdue_count'] += 1

        # Convertir a lista y ordenar
        partners_summary = []
        for data in partners_data.values():
            partners_summary.append(data)
            total_global_invoices += data['total_invoices']
            total_global_payments += data['total_payments']
            total_global_balance += data['total_balance']

        partners_summary.sort(key=lambda x: x['partner'].name)

        ctx.update({
            'view_mode': 'consolidated',
            'partners_summary': partners_summary,
            'total_global_invoices': total_global_invoices,
            'total_global_payments': total_global_payments,
            'total_global_balance': total_global_balance,
            'partners_count': len(partners_summary),
        })
        return ctx