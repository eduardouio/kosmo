from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Sum
from collections import defaultdict
import json
from trade.models import Invoice, PaymentDetail
from partners.models import Partner


class CollectionsReportsView(View):
    template_name = 'reports/collections_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get(
            'date_from', start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        partner_id = request.GET.get('partner_id', '')

        # Construir query base para facturas de venta
        invoices_query = Invoice.objects.filter(
            type_document='FAC_VENTA',
            date__date__range=[date_from, date_to]
        ).select_related('partner', 'order')

        # Aplicar filtro de partner si se especifica
        if partner_id:
            invoices_query = invoices_query.filter(partner_id=partner_id)

        # Obtener facturas
        invoices = invoices_query.order_by('-date')

        # Calcular estadísticas básicas
        total_invoices = invoices.count()
        # Calcular total_amount sumando el monto con margen incluido
        total_amount = 0
        for invoice in invoices:
            total_amount += invoice.total_invoice

        # Top de clientes con más facturas
        top_customers = []
        if invoices.exists():
            customer_stats = {}
            for invoice in invoices:
                partner_id_iter = invoice.partner.id
                partner_name = invoice.partner.name

                if partner_id_iter not in customer_stats:
                    customer_stats[partner_id_iter] = {
                        'name': partner_name,
                        'count': 0,
                        'total': 0
                    }
                customer_stats[partner_id_iter]['count'] += 1
                customer_stats[partner_id_iter]['total'] += float(
                    invoice.total_invoice)

            # Ordenar por monto total y tomar top 5
            top_customers = sorted(
                customer_stats.values(),
                key=lambda x: x['total'],
                reverse=True
            )[:5]

        # Calcular facturas por semana
        weekly_invoices = defaultdict(lambda: {'count': 0, 'total': 0})

        if invoices.exists():
            for invoice in invoices:
                # Obtener el inicio de la semana (lunes)
                # Asegurar que la fecha sea un date, no datetime
                invoice_date = invoice.date
                if hasattr(invoice_date, 'date'):
                    invoice_date = invoice_date.date()

                week_start = invoice_date - \
                    timedelta(days=invoice_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                weekly_invoices[week_key]['count'] += 1
                weekly_invoices[week_key]['total'] += float(
                    invoice.total_invoice)

        # Convertir a lista ordenada para el gráfico
        weekly_data = []
        for week, data in sorted(weekly_invoices.items()):
            week_date = datetime.strptime(week, '%Y-%m-%d')
            week_label = week_date.strftime('%d/%m')
            weekly_data.append({
                'week': week_label,
                'total': data['total'],
                'count': data['count']
            })

        # Agregar información adicional a cada factura para la tabla
        for invoice in invoices:
            # Obtener el nombre del usuario creador
            user_creator = invoice.user_creator
            if user_creator:
                invoice.creator_name = user_creator.get_full_name()
            else:
                invoice.creator_name = 'Sistema'

            # Calcular monto cobrado de esta factura
            paid_amount = PaymentDetail.objects.filter(
                invoice=invoice
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            invoice.paid_amount = float(paid_amount)
            invoice.balance = float(invoice.total_invoice) - float(paid_amount)

            # Calcular días de vencimiento
            if invoice.due_date and invoice.status == 'PENDIENTE':
                today = timezone.now().date()
                # Asegurar que due_date sea un date, no datetime
                due_date = invoice.due_date
                if hasattr(due_date, 'date'):
                    due_date = due_date.date()
                
                days_diff = (due_date - today).days
                if days_diff < 0:
                    invoice.is_overdue = True
                    invoice.calculated_days_overdue = abs(days_diff)
                else:
                    invoice.is_overdue = False
                    invoice.calculated_days_to_due = days_diff
            else:
                invoice.is_overdue = False

        # Obtener listas para filtros (clientes)
        partners = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')

        # Estadísticas adicionales
        paid_invoices = invoices.filter(status='PAGADO')
        total_paid = 0
        for invoice in paid_invoices:
            total_paid += invoice.total_invoice

        pending_invoices = invoices.filter(status='PENDIENTE')
        total_pending = 0
        for invoice in pending_invoices:
            total_pending += invoice.total_invoice

        overdue_invoices = invoices.filter(
            status='PENDIENTE',
            due_date__lt=timezone.now()
        )
        total_overdue = 0
        for invoice in overdue_invoices:
            total_overdue += invoice.total_invoice

        context = {
            'title_page': 'Reporte de Cobros',
            'invoices': invoices,
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_pending': total_pending,
            'total_overdue': total_overdue,
            'top_customers': top_customers,
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
