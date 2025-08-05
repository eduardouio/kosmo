from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from trade.models import Payment, PaymentDetail
from partners.models import Partner


class PymenReportView(View):
    template_name = 'reports/pymen_report.html'
    
    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from', 
                                   start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        partner_id = request.GET.get('partner_id', '')
        payment_method = request.GET.get('payment_method', '')
        status = request.GET.get('status', '')
        transaction_type = request.GET.get('transaction_type', '')

        # Construir query base
        payments_query = Payment.objects.filter(
            date__range=[date_from, date_to]
        ).select_related('processed_by', 'approved_by')

        # Aplicar filtros adicionales
        if payment_method:
            payments_query = payments_query.filter(method=payment_method)
        if status:
            payments_query = payments_query.filter(status=status)
        if transaction_type:
            payments_query = payments_query.filter(
                type_transaction=transaction_type)

        # Obtener pagos
        payments = payments_query.order_by('-date')

        # Calcular estadísticas
        total_payments = payments.count()
        total_ingresos = payments.filter(
            type_transaction='INGRESO'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_egresos = payments.filter(
            type_transaction='EGRESO'
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        # Agrupar por estado
        status_summary = payments.values('status').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('status')

        # Agrupar por método de pago
        method_summary = payments.values('method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')

        # Agrupar por tipo de transacción
        type_summary = payments.values('type_transaction').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('type_transaction')

        # Obtener listas para filtros
        partners = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Pagos',
            'payments': payments,
            'total_payments': total_payments,
            'total_ingresos': total_ingresos,
            'total_egresos': total_egresos,
            'balance': total_ingresos - total_egresos,
            'status_summary': status_summary,
            'method_summary': method_summary,
            'type_summary': type_summary,
            'partners': partners,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'partner_id': partner_id,
                'payment_method': payment_method,
                'status': status,
                'transaction_type': transaction_type,
            },
            'status_choices': Payment._meta.get_field('status').choices,
            'method_choices': Payment._meta.get_field('method').choices,
            'type_choices': Payment._meta.get_field(
                'type_transaction').choices,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
