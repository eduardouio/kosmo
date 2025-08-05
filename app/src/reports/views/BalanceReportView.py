from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from trade.models import Order, Invoice, Payment
from partners.models import Partner
from decimal import Decimal
import json


class BalanceReportView(View):
    template_name = 'reports/balance_report.html'

    def get(self, request, *args, **kwargs):
        # Filtros de fechas por defecto (último mes)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30)

        # Obtener parámetros de filtro
        date_from = request.GET.get('date_from',
                                    start_date.strftime('%Y-%m-%d'))
        date_to = request.GET.get('date_to', end_date.strftime('%Y-%m-%d'))

        # === ANÁLISIS DE COMPRAS ===
        purchase_orders = Order.objects.filter(
            type_document='ORD_COMPRA',
            date__date__range=[date_from, date_to],
            status__in=['CONFIRMADO', 'FACTURADO']
        )

        total_compras = purchase_orders.aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        count_compras = purchase_orders.count()

        # Compras por proveedor
        compras_por_proveedor = purchase_orders.values(
            'partner__name'
        ).annotate(
            total=Sum('total_price'),
            count=Count('id')
        ).order_by('-total')[:10]

        # === ANÁLISIS DE VENTAS ===
        sales_orders = Order.objects.filter(
            type_document='ORD_VENTA',
            date__date__range=[date_from, date_to],
            status__in=['CONFIRMADO', 'FACTURADO']
        )

        total_ventas = sales_orders.aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        total_margen = sales_orders.aggregate(
            Sum('total_margin'))['total_margin__sum'] or Decimal('0')
        count_ventas = sales_orders.count()

        # Ventas por cliente
        ventas_por_cliente = sales_orders.values(
            'partner__name'
        ).annotate(
            total=Sum('total_price'),
            margin=Sum('total_margin'),
            count=Count('id')
        ).order_by('-total')[:10]

        # === ANÁLISIS DE PAGOS ===
        payments = Payment.objects.filter(
            date__range=[date_from, date_to],
            status='CONFIRMADO'
        )

        ingresos = payments.filter(
            type_transaction='INGRESO'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        egresos = payments.filter(
            type_transaction='EGRESO'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')

        # === CÁLCULOS DE BALANCE ===
        utilidad_bruta = total_ventas - total_compras
        rentabilidad = (utilidad_bruta / total_ventas *
                        100) if total_ventas > 0 else 0
        flujo_efectivo = ingresos - egresos

        # Margen de contribución
        margen_contribucion = (
            total_margen / total_ventas * 100) if total_ventas > 0 else 0

        # === ANÁLISIS TEMPORAL ===
        # Compras y ventas por mes (últimos 6 meses para gráfico)
        monthly_data = []
        for i in range(6):
            month_start = end_date.replace(day=1) - timedelta(days=i*30)
            month_end = (month_start + timedelta(days=32)
                         ).replace(day=1) - timedelta(days=1)

            month_purchases = Order.objects.filter(
                type_document='ORD_COMPRA',
                date__date__range=[month_start, month_end],
                status__in=['CONFIRMADO', 'FACTURADO']
            ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

            month_sales = Order.objects.filter(
                type_document='ORD_VENTA',
                date__date__range=[month_start, month_end],
                status__in=['CONFIRMADO', 'FACTURADO']
            ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

            monthly_data.append({
                'month': month_start.strftime('%m/%Y'),
                'purchases': float(month_purchases),
                'sales': float(month_sales),
                'profit': float(month_sales - month_purchases)
            })

        monthly_data.reverse()  # Ordenar cronológicamente

        # === INDICADORES KPI ===
        kpis = {
            'roi': (utilidad_bruta / total_compras * 100) if total_compras > 0 else 0,
            'ticket_promedio_venta': (total_ventas / count_ventas) if count_ventas > 0 else 0,
            'ticket_promedio_compra': (total_compras / count_compras) if count_compras > 0 else 0,
            'ratio_ventas_compras': (total_ventas / total_compras) if total_compras > 0 else 0,
        }

        context = {
            'title_page': 'Balance Financiero',
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
            },
            # Datos de compras
            'total_compras': total_compras,
            'count_compras': count_compras,
            'compras_por_proveedor': compras_por_proveedor,

            # Datos de ventas
            'total_ventas': total_ventas,
            'total_margen': total_margen,
            'count_ventas': count_ventas,
            'ventas_por_cliente': ventas_por_cliente,

            # Datos de pagos
            'ingresos': ingresos,
            'egresos': egresos,
            'flujo_efectivo': flujo_efectivo,

            # Balance y KPIs
            'utilidad_bruta': utilidad_bruta,
            'rentabilidad': rentabilidad,
            'margen_contribucion': margen_contribucion,
            'kpis': kpis,

            # Datos temporales - convertir a JSON string
            'monthly_data_json': json.dumps(monthly_data),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
