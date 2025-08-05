from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from trade.models import Invoice, Payment, PaymentDetail
from partners.models import Partner


class CollectionsReportsView(View):
    template_name = 'reports/collections_report.html'
    
    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from', 
                                   start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        customer_id = request.GET.get('customer_id', '')
        status = request.GET.get('status', '')

        # Construir query base para facturas de venta
        invoices_query = Invoice.objects.filter(
            type_document='FAC_VENTA',
            date__date__range=[date_from, date_to]
        ).select_related('partner', 'order')

        # Aplicar filtros adicionales
        if customer_id:
            invoices_query = invoices_query.filter(partner_id=customer_id)
        if status:
            invoices_query = invoices_query.filter(status=status)

        # Obtener facturas
        invoices = invoices_query.order_by('-date')

        # Calcular estadísticas
        total_invoices = invoices.count()
        total_facturado = invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or 0
        
        # Facturas pagadas
        paid_invoices = invoices.filter(status='PAGADO')
        total_cobrado = paid_invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or 0
        
        # Facturas pendientes
        pending_invoices = invoices.filter(status='PENDIENTE')
        total_pendiente = pending_invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or 0

        # Agrupar por estado
        status_summary = invoices.values('status').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('status')

        # Agrupar por cliente
        customer_summary = invoices.values(
            'partner__name',
            'partner_id'
        ).annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:10]  # Top 10 clientes

        # Facturas vencidas (pendientes con fecha de vencimiento pasada)
        overdue_invoices = invoices.filter(
            status='PENDIENTE',
            due_date__lt=timezone.now().date()
        )
        total_vencido = overdue_invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or 0

        # Obtener listas para filtros
        customers = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Cobros',
            'invoices': invoices,
            'total_invoices': total_invoices,
            'total_facturado': total_facturado,
            'total_cobrado': total_cobrado,
            'total_pendiente': total_pendiente,
            'total_vencido': total_vencido,
            'overdue_invoices': overdue_invoices,
            'status_summary': status_summary,
            'customer_summary': customer_summary,
            'customers': customers,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'customer_id': customer_id,
                'status': status,
            },
            'status_choices': Invoice._meta.get_field('status').choices,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})