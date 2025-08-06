from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from trade.models import Order, Invoice
from partners.models import Partner
from products.models import Product


class SalesReportView(View):
    template_name = 'reports/sales_report.html'
    
    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)
        
        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from', 
                                   start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        customer_id = request.GET.get('customer_id', '')
        product_id = request.GET.get('product_id', '')
        status = request.GET.get('status', '')

        # Construir query base para órdenes de venta
        orders_query = Order.objects.filter(
            type_document='ORD_VENTA',
            date__date__range=[date_from, date_to]
        ).select_related('partner').prefetch_related(
            'orderitems_set__orderboxitems_set__product'
        )

        # Aplicar filtros adicionales
        if customer_id:
            orders_query = orders_query.filter(partner_id=customer_id)
        if status:
            orders_query = orders_query.filter(status=status)

        # Obtener órdenes de venta
        sales_orders = orders_query.order_by('-date')

        # Calcular estadísticas
        total_orders = sales_orders.count()
        total_amount = sales_orders.aggregate(
            Sum('total_price'))['total_price__sum'] or 0
        total_margin = sales_orders.aggregate(
            Sum('total_margin'))['total_margin__sum'] or 0
        
        # Agrupar por estado
        status_summary = sales_orders.values('status').annotate(
            count=Count('id'),
            total=Sum('total_price')
        ).order_by('status')

        # Agrupar por cliente
        customer_summary = sales_orders.values(
            'partner__name',
            'partner_id'
        ).annotate(
            count=Count('id'),
            total=Sum('total_price'),
            margin=Sum('total_margin')
        ).order_by('-total')[:10]  # Top 10 clientes

        # Obtener listas para filtros
        customers = Partner.objects.filter(
            business_tax_id__isnull=False
        ).order_by('name')
        
        products = Product.objects.filter(
            is_active=True
        ).order_by('name')

        context = {
            'title_page': 'Reporte de Ventas',
            'sales_orders': sales_orders,
            'total_orders': total_orders,
            'total_amount': total_amount,
            'total_margin': total_margin,
            'status_summary': status_summary,
            'customer_summary': customer_summary,
            'customers': customers,
            'products': products,
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'customer_id': customer_id,
                'product_id': product_id,
                'status': status,
            },
            'status_choices': Order._meta.get_field('status').choices,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
