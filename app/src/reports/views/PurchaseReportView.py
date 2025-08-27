from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from trade.models import Invoice
from partners.models import Partner
from products.models import Product


class PurchaseReportView(View):
    template_name = 'reports/purchase_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get(
            'date_from', start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        supplier_id = request.GET.get('supplier_id', '')
        product_id = request.GET.get('product_id', '')
        status = request.GET.get('status', '')

        # Construir query base para facturas de compra
        invoices_query = Invoice.objects.filter(
            type_document='FAC_COMPRA',
            date__date__range=[date_from, date_to]
        ).select_related('partner').prefetch_related(
            'invoiceitems_set__invoiceboxitems_set__product'
        )

        # Aplicar filtros adicionales
        if supplier_id:
            invoices_query = invoices_query.filter(partner_id=supplier_id)
        if status:
            invoices_query = invoices_query.filter(status=status)

        # Obtener facturas de compra
        purchase_invoices = invoices_query.order_by('-date')

        # Calcular estadísticas (solo precio, sin margen para compras)
        total_invoices = purchase_invoices.count()
        total_amount = purchase_invoices.aggregate(Sum('total_price'))[
            'total_price__sum'] or 0

        # Agrupar por estado
        status_summary = purchase_invoices.values('status').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('status')

        # Agrupar por proveedor
        supplier_summary = purchase_invoices.values(
            'partner__name',
            'partner_id'
        ).annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('-total')[:10]  # Top 10 proveedores

        # Obtener listas para filtros
        suppliers = Partner.objects.filter(
            type_partner='PROVEEDOR',
            is_active=True
        ).order_by('name')

        products = Product.objects.filter(
            is_active=True
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Facturas de Compra',
            'purchase_invoices': purchase_invoices,
            'total_invoices': total_invoices,
            'total_amount': total_amount,
            'status_summary': status_summary,
            'supplier_summary': supplier_summary,
            'suppliers': suppliers,
            'products': products,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'supplier_id': supplier_id,
                'product_id': product_id,
                'status': status,
            },
            'status_choices': Invoice._meta.get_field('status').choices,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"
        })
