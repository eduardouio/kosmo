from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from trade.models import Invoice
from partners.models import Partner
from products.models import Product


class SalesReportView(View):
    template_name = 'reports/sales_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from', start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        customer_id = request.GET.get('customer_id', '')
        product_id = request.GET.get('product_id', '')

        # Construir query base para facturas de venta
        invoices_query = Invoice.objects.filter(
            type_document='FAC_VENTA',
            is_active=True,
            date__date__range=[date_from, date_to]
        ).select_related('partner').prefetch_related(
            'invoiceitems_set__invoiceboxitems_set__product'
        )

        # Aplicar filtros adicionales
        if customer_id:
            invoices_query = invoices_query.filter(partner_id=customer_id)

        # Obtener facturas de venta ordenadas por fecha de vencimiento de menor a mayor y luego por fecha descendente
        sales_invoices = invoices_query.order_by('due_date', '-date')

        # Agregar información de vencimiento a cada factura
        current_date = timezone.now().date()
        for invoice in sales_invoices:
            if invoice.due_date:
                due_date = invoice.due_date.date()
                if due_date < current_date and invoice.status == 'PENDIENTE':
                    invoice.is_invoice_overdue = True
                    invoice.days_invoice_overdue = (
                        current_date - due_date
                    ).days
                    invoice.days_invoice_to_due = 0
                    invoice.sort_order = -invoice.days_invoice_overdue
                else:
                    invoice.is_invoice_overdue = False
                    invoice.days_invoice_overdue = 0
                    invoice.days_invoice_to_due = (
                        due_date - current_date
                    ).days
                    invoice.sort_order = invoice.days_invoice_to_due
            else:
                invoice.is_invoice_overdue = False
                invoice.days_invoice_overdue = 0
                invoice.days_invoice_to_due = 0
                invoice.sort_order = 99999  # Sin fecha

        # Agrupar por estado de TODAS las facturas de venta (no solo rango)
        all_sales_invoices = Invoice.objects.filter(
            type_document='FAC_VENTA'
        )
        
        # Para ventas, sumar total_price + total_margin
        status_data = []
        for status_item in all_sales_invoices.values('status').annotate(
            count=Count('id'),
            total_base=Sum('total_price'),
            total_margin_sum=Sum('total_margin')
        ):
            total_with_margin = (status_item['total_base'] or 0) + (
                status_item['total_margin_sum'] or 0
            )
            status_data.append({
                'status': status_item['status'],
                'count': status_item['count'],
                'total': total_with_margin
            })

        # Calcular facturas vencidas de venta (todas, no solo del rango)
        current_date = timezone.now().date()
        overdue_invoices = Invoice.objects.filter(
            type_document='FAC_VENTA',
            due_date__isnull=False,
            due_date__date__lt=current_date,
            status__in=['PENDIENTE']  # Solo pendientes pueden estar vencidas
        )
        
        overdue_count = overdue_invoices.count()
        overdue_total = sum([
            inv.total_price + inv.total_margin for inv in overdue_invoices
        ])

        # Crear lista completa con todos los estados del modelo
        all_status = dict(Invoice._meta.get_field('status').choices)
        status_summary = []
        
        # Convertir status_data a diccionario para acceso rápido
        status_dict = {item['status']: item for item in status_data}
        
        # Agregar todos los estados definidos en el modelo
        for status_key, status_label in all_status.items():
            if status_key in status_dict:
                status_summary.append({
                    'status': status_key,
                    'status_label': status_label,
                    'count': status_dict[status_key]['count'],
                    'total': status_dict[status_key]['total'] or 0
                })
            else:
                status_summary.append({
                    'status': status_key,
                    'status_label': status_label,
                    'count': 0,
                    'total': 0
                })
        
        # Agregar estado "VENCIDO" calculado
        status_summary.append({
            'status': 'VENCIDO',
            'status_label': 'VENCIDO',
            'count': overdue_count,
            'total': overdue_total
        })

        # Agrupar por cliente - calcular total con margen incluido
        customer_summary = []
        customer_data = sales_invoices.values(
            'partner__name', 'partner_id'
        ).annotate(
            count=Count('id'),
            total_base=Sum('total_price'),
            total_margin_sum=Sum('total_margin')
        ).order_by('-total_base')[:10]
        
        for invoice_data in customer_data:
            total_with_margin = (
                (invoice_data['total_base'] or 0) +
                (invoice_data['total_margin_sum'] or 0)
            )
            customer_summary.append({
                'partner__name': invoice_data['partner__name'],
                'partner_id': invoice_data['partner_id'],
                'count': invoice_data['count'],
                'total': total_with_margin
            })

        # Obtener listas para filtros - solo clientes con facturas
        customers = Partner.objects.filter(
            business_tax_id__isnull=False,
            is_active=True,
            id__in=Invoice.objects.filter(
                type_document='FAC_VENTA'
            ).values_list('partner_id', flat=True).distinct()
        ).order_by('name')
        
        products = Product.objects.filter(
            is_active=True
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Facturas de Venta',
            'sales_invoices': sales_invoices,
            'status_summary': status_summary,
            'customer_summary': customer_summary,
            'customers': customers,
            'products': products,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'customer_id': customer_id,
                'product_id': product_id,
            },
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
