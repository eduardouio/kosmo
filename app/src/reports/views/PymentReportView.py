from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum
from collections import defaultdict
import json
from trade.models import Payment
from partners.models import Partner


class PymentReportView(View):
    template_name = 'reports/pyment_report.html'

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
        total_amount = payments.aggregate(total=Sum('amount'))['total'] or 0

        # Top de proveedores con más pagos
        top_providers = []
        if payments.exists():
            provider_stats = {}
            for payment in payments:
                # Obtener proveedores de las facturas asociadas
                payment_partners = payment.invoices.values_list(
                    'invoice__partner__name',
                    'invoice__partner__id'
                ).distinct()

                for partner_name, partner_id_iter in payment_partners:
                    # Verificar que no sean None
                    if partner_id_iter and partner_name:
                        if partner_id_iter not in provider_stats:
                            provider_stats[partner_id_iter] = {
                                'name': partner_name,
                                'count': 0,
                                'total': 0
                            }
                        provider_stats[partner_id_iter]['count'] += 1
                        amount = float(payment.amount) if payment.amount else 0
                        provider_stats[partner_id_iter]['total'] += amount

            # Ordenar por monto total y tomar top 5
            top_providers = sorted(
                provider_stats.values(),
                key=lambda x: x['total'],
                reverse=True
            )[:5]        # Calcular pagos por semana
        weekly_payments = defaultdict(lambda: {'count': 0, 'total': 0})
        
        if payments.exists():
            for payment in payments:
                # Obtener el inicio de la semana (lunes)
                week_start = payment.date - timedelta(
                    days=payment.date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                weekly_payments[week_key]['count'] += 1
                amount = float(payment.amount) if payment.amount else 0
                weekly_payments[week_key]['total'] += amount
        
        # Convertir a lista ordenada para el gráfico
        weekly_data = []
        for week, data in sorted(weekly_payments.items()):
            week_date = datetime.strptime(week, '%Y-%m-%d')
            week_label = week_date.strftime('%d/%m')
            weekly_data.append({
                'week': week_label,
                'total': data['total'],
                'count': data['count']
            })

        # Agregar información adicional a cada pago para la tabla
        for payment in payments:
            # Obtener nombres de partners asociados
            partners_list = payment.invoices.values_list(
                'invoice__partner__name', flat=True
            ).distinct()
            payment.display_partners = ', '.join(
                [p for p in partners_list if p])

            # Calcular monto aplicado a facturas y saldo
            applied_amount = payment.invoices.aggregate(
                total=Sum('amount'))['total'] or 0
            payment.applied_amount = float(applied_amount)
            payment.balance = float(payment.amount) - float(applied_amount)

            # Obtener el nombre del usuario creador
            user_creator = payment.user_creator
            if user_creator:
                payment.creator_name = user_creator.get_full_name()
            else:
                payment.creator_name = 'Sistema'

        # Obtener listas para filtros
        partners = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Pagos',
            'payments': payments,
            'total_payments': total_payments,
            'total_amount': total_amount,
            'top_providers': top_providers,
            'weekly_data_json': json.dumps(weekly_data),
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
