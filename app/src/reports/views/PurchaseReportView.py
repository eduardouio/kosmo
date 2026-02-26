from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import timedelta, datetime
from trade.models import Invoice
from partners.models import Partner
from products.models import Product


class PurchaseReportView(LoginRequiredMixin, View):
    template_name = 'reports/purchase_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from_param = request.GET.get('date_from')
        date_to_param = request.GET.get('date_to')
        supplier_id = request.GET.get('supplier_id', '')
        product_id = request.GET.get('product_id', '')

        def parse_date(value, default):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except (TypeError, ValueError):
                return default

        date_from = parse_date(date_from_param, start_date)
        date_to = parse_date(date_to_param, end_date)

        if date_from > date_to:
            date_from, date_to = date_to, date_from

        # Construir query base para facturas de compra CON FILTRO DE FECHAS APLICADO SIEMPRE
        invoices_query = Invoice.objects.filter(
            type_document='FAC_COMPRA',
            is_active=True,
            date__date__range=[date_from, date_to]  # Filtro de fechas aplicado desde el inicio
        ).select_related('partner').prefetch_related(
            'invoiceitems_set__invoiceboxitems_set__product'
        )

        # Aplicar filtro de proveedor SI está seleccionado
        if supplier_id and supplier_id != '':
            try:
                supplier_id_int = int(supplier_id)
                invoices_query = invoices_query.filter(partner_id=supplier_id_int)
            except (ValueError, TypeError):
                # Si supplier_id no es un entero válido, no filtrar por proveedor
                pass

        # Obtener facturas de compra ordenadas por fecha de vencimiento
        purchase_invoices = invoices_query.order_by('due_date', '-date')

        # Agregar información de vencimiento a cada factura
        current_date = timezone.now().date()
        for invoice in purchase_invoices:
            if invoice.due_date:
                due_date = invoice.due_date.date()
                if due_date < current_date and invoice.status == 'PENDIENTE':
                    invoice.is_invoice_overdue = True
                    invoice.days_invoice_overdue = (
                        current_date - due_date
                    ).days
                    invoice.days_invoice_to_due = 0
                else:
                    invoice.is_invoice_overdue = False
                    invoice.days_invoice_overdue = 0
                    invoice.days_invoice_to_due = (
                        due_date - current_date
                    ).days
            else:
                invoice.is_invoice_overdue = False
                invoice.days_invoice_overdue = 0
                invoice.days_invoice_to_due = 0

        # Agrupar por estado dentro del rango seleccionado (usar la misma query filtrada)
        status_data = invoices_query.values('status').annotate(
            count=Count('id'),
            total=Sum('total_price'),
            qb_total=Sum('qb_total'),
            hb_total=Sum('hb_total'),
            eb_total=Sum('eb_total'),
            stems_total=Sum('tot_stem_flower')
        )

        # Calcular facturas vencidas SOLO del rango de fechas seleccionado
        overdue_invoices = invoices_query.filter(
            due_date__isnull=False,
            due_date__date__lt=current_date,
            status__in=['PENDIENTE']  # Solo pendientes pueden estar vencidas
        )

        overdue_aggregate = overdue_invoices.aggregate(
            total=Sum('total_price'),
            qb_total=Sum('qb_total'),
            hb_total=Sum('hb_total'),
            eb_total=Sum('eb_total'),
            stems_total=Sum('tot_stem_flower')
        )
        overdue_count = overdue_invoices.count()
        overdue_total = overdue_aggregate['total'] or 0
        overdue_qb_total = overdue_aggregate['qb_total'] or 0
        overdue_hb_total = overdue_aggregate['hb_total'] or 0
        overdue_eb_total = overdue_aggregate['eb_total'] or 0
        overdue_stems_total = overdue_aggregate['stems_total'] or 0

        # Crear lista completa con todos los estados del modelo
        all_status = dict(Invoice._meta.get_field('status').choices)
        status_summary = []

        # Convertir status_data a diccionario para acceso rápido
        status_dict = {item['status']: item for item in status_data}

        # Agregar todos los estados definidos en el modelo
        for status_key, status_label in all_status.items():
            item = status_dict.get(status_key)
            status_summary.append({
                'status': status_key,
                'status_label': status_label,
                'count': item['count'] if item else 0,
                'total': (item['total'] or 0) if item else 0,
                'qb_total': (item['qb_total'] or 0) if item else 0,
                'hb_total': (item['hb_total'] or 0) if item else 0,
                'eb_total': (item['eb_total'] or 0) if item else 0,
                'stems_total': (item['stems_total'] or 0) if item else 0,
            })

        # Agregar estado "VENCIDO" calculado
        status_summary.append({
            'status': 'VENCIDO',
            'status_label': 'VENCIDO',
            'count': overdue_count,
            'total': overdue_total,
            'qb_total': overdue_qb_total,
            'hb_total': overdue_hb_total,
            'eb_total': overdue_eb_total,
            'stems_total': overdue_stems_total,
        })

        # Agrupar por proveedor (usar la misma query filtrada)
        supplier_summary = invoices_query.values(
            'partner__name',
            'partner_id'
        ).annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:10]  # Top 10 proveedores

        # Obtener listas para filtros - solo proveedores con facturas
        suppliers = Partner.objects.filter(
            type_partner='PROVEEDOR',
            is_active=True,
            id__in=Invoice.objects.filter(
                type_document='FAC_COMPRA'
            ).values_list('partner_id', flat=True).distinct()
        ).order_by('name')

        products = Product.objects.filter(
            is_active=True
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Facturas de Compra',
            'purchase_invoices': purchase_invoices,
            'status_summary': status_summary,
            'supplier_summary': supplier_summary,
            'suppliers': suppliers,
            'products': products,
            'filters': {
                'date_from': date_from.strftime('%Y-%m-%d'),
                'date_to': date_to.strftime('%Y-%m-%d'),
                'supplier_id': supplier_id,
                'product_id': product_id,
            },
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"
        })
        return JsonResponse({
            "message": "Export functionality to be implemented"
        })
