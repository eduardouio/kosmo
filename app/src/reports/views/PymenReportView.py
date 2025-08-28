from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from trade.models import Payment
from partners.models import Partner


class PymenReportView(View):
    template_name = 'reports/pymen_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get(
            'date_from', start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        partner_id = request.GET.get('partner_id', '')

        # Construir query base
        payments_query = Payment.objects.filter(
            date__range=[date_from, date_to]
        ).select_related('processed_by', 'approved_by').prefetch_related(
            'invoices__invoice__partner'
        )

        # Aplicar filtro de partner si se especifica
        if partner_id:
            payments_query = payments_query.filter(
                invoices__invoice__partner_id=partner_id
            ).distinct()

        # Obtener pagos
        payments = payments_query.order_by('-date')

        # Calcular estadísticas básicas
        total_payments = payments.count()

        # Obtener listas para filtros
        partners = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Pagos',
            'payments': payments,
            'total_payments': total_payments,
            'partners': partners,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'partner_id': partner_id,
            },
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
