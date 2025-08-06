from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from trade.models import OrderBoxItems
from products.models import Product
from decimal import Decimal
import json


class SalesByProductReportView(View):
    template_name = 'reports/sales_by_product_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from',
                                    start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))
        product_id = request.GET.get('product_id', '')
        variety = request.GET.get('variety', '')

        # === ANÁLISIS DE PRODUCTOS VENDIDOS ===
        # Obtener productos vendidos basado en OrderBoxItems de ventas
        product_sales_query = OrderBoxItems.objects.filter(
            order_item__order__type_document='ORD_VENTA',
            order_item__order__date__date__range=[date_from, date_to],
            order_item__order__status__in=['CONFIRMADO', 'FACTURADO']
        ).select_related('product', 'order_item__order__partner')

        # Aplicar filtros adicionales
        if product_id:
            product_sales_query = product_sales_query.filter(
                product_id=product_id)
        if variety:
            product_sales_query = product_sales_query.filter(
                product__variety__icontains=variety)

        # Agrupar ventas por producto
        product_sales = product_sales_query.values(
            'product__id',
            'product__name',
            'product__variety',
            'product__colors'
        ).annotate(
            total_stems=Sum('qty_stem_flower'),
            total_bunches=Sum('total_bunches'),
            total_boxes=Count('order_item__id'),
            total_orders=Count('order_item__order__id', distinct=True),
            total_revenue=Sum('order_item__line_total'),
            total_cost=Sum('order_item__line_price'),
            total_margin=Sum('order_item__line_margin'),
            avg_price_per_stem=Avg('stem_cost_price'),
            total_customers=Count(
                'order_item__order__partner__id', distinct=True)
        ).order_by('-total_revenue')

        # === ANÁLISIS DE PRODUCTOS COMPRADOS ===
        # Obtener productos comprados basado en OrderBoxItems de compras
        product_purchases = OrderBoxItems.objects.filter(
            order_item__order__type_document='ORD_COMPRA',
            order_item__order__date__date__range=[date_from, date_to],
            order_item__order__status__in=['CONFIRMADO', 'FACTURADO']
        ).values(
            'product__id',
            'product__name',
            'product__variety'
        ).annotate(
            total_stems_purchased=Sum('qty_stem_flower'),
            total_bunches_purchased=Sum('total_bunches'),
            total_cost_purchased=Sum('order_item__line_price'),
            total_orders_purchased=Count(
                'order_item__order__id', distinct=True),
            total_suppliers=Count(
                'order_item__order__partner__id', distinct=True)
        ).order_by('-total_cost_purchased')

        # === ESTADÍSTICAS GENERALES ===
        total_products_sold = product_sales.count()
        total_stems_sold = product_sales_query.aggregate(
            Sum('qty_stem_flower'))['qty_stem_flower__sum'] or 0
        total_revenue = product_sales_query.values(
            'order_item'
        ).distinct().aggregate(
            Sum('order_item__line_total')
        )['order_item__line_total__sum'] or Decimal('0')

        # === TOP PRODUCTOS ===
        top_products_by_revenue = product_sales[:10]
        top_products_by_volume = product_sales.order_by('-total_stems')[:10]

        # === ANÁLISIS POR VARIEDAD ===
        # Crear un nuevo queryset específico para análisis por variedad
        varieties_analysis = OrderBoxItems.objects.filter(
            order_item__order__type_document='ORD_VENTA',
            order_item__order__date__date__range=[date_from, date_to],
            order_item__order__status__in=['CONFIRMADO', 'FACTURADO']
        )
        
        # Aplicar los mismos filtros si existen
        if product_id:
            varieties_analysis = varieties_analysis.filter(
                product_id=product_id)
        if variety:
            varieties_analysis = varieties_analysis.filter(
                product__variety__icontains=variety)
            
        varieties_analysis = varieties_analysis.values(
            'product__variety'
        ).annotate(
            variety_stems=Sum('qty_stem_flower'),
            variety_revenue=Sum('order_item__line_total'),
            variety_products=Count('product__id', distinct=True),
            variety_orders=Count('order_item__order__id', distinct=True)
        ).order_by('-variety_revenue')[:15]

        # Calcular el promedio por orden para cada variedad
        varieties_with_avg = []
        for variety in varieties_analysis:
            avg_revenue_per_order = (
                variety['variety_revenue'] / variety['variety_orders']
                if variety['variety_orders'] > 0 else 0
            )
            variety['avg_revenue_per_order'] = avg_revenue_per_order
            varieties_with_avg.append(variety)

        # === PRODUCTOS MÁS RENTABLES ===
        most_profitable = []
        for product in product_sales:
            if product['total_cost'] and product['total_cost'] > 0:
                roi = (product['total_margin'] / product['total_cost'] * 100)
                most_profitable.append({
                    'product': product,
                    'roi': roi
                })
        most_profitable = sorted(
            most_profitable, key=lambda x: x['roi'], reverse=True)[:10]

        # === ANÁLISIS TEMPORAL ===
        monthly_data = []
        for i in range(6):
            month_start = end_date.replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)
                         ).replace(day=1) - timedelta(days=1)

            month_sales = OrderBoxItems.objects.filter(
                order_item__order__type_document='ORD_VENTA',
                order_item__order__date__date__range=[month_start, month_end],
                order_item__order__status__in=['CONFIRMADO', 'FACTURADO']
            ).aggregate(
                stems=Sum('qty_stem_flower'),
                revenue=Sum('order_item__line_total')
            )

            monthly_data.append({
                'month': month_start.strftime('%m/%Y'),
                'stems': int(month_sales['stems'] or 0),
                'revenue': float(month_sales['revenue'] or 0)
            })

        monthly_data.reverse()

        # Obtener listas para filtros
        products = Product.objects.filter(is_active=True).order_by('name')
        varieties = Product.objects.filter(is_active=True).values_list(
            'variety', flat=True).distinct().order_by('variety')

        context = {
            'title_page': 'Reporte de Productos',
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
                'product_id': product_id,
                'variety': variety,
            },

            # Estadísticas generales
            'total_products_sold': total_products_sold,
            'total_stems_sold': total_stems_sold,
            'total_revenue': total_revenue,

            # Datos principales
            'product_sales': product_sales,
            'product_purchases': product_purchases,

            # Top productos
            'top_products_by_revenue': top_products_by_revenue,
            'top_products_by_volume': top_products_by_volume,
            'most_profitable': most_profitable,

            # Análisis por variedad
            'varieties_analysis': varieties_with_avg,

            # Listas para filtros
            'products': products,
            'varieties': varieties,

            # Datos temporales
            'monthly_data_json': json.dumps(monthly_data),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
