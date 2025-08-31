from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from trade.models import Order, Payment
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

        # Total de ventas (precio base + margen) y margen real obtenido
        total_price_base = sales_orders.aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        total_margen = sales_orders.aggregate(
            Sum('total_margin'))['total_margin__sum'] or Decimal('0')
        # Total de ventas real incluye el margen
        total_ventas = total_price_base + total_margen
        count_ventas = sales_orders.count()

        # Ventas por cliente (incluyendo margen real)
        ventas_por_cliente = sales_orders.values(
            'partner__name'
        ).annotate(
            total=Sum('total_price'),
            margin=Sum('total_margin'),  # Margen real obtenido por cliente
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
        # La utilidad bruta es el margen real obtenido en las ventas
        utilidad_bruta = total_margen

        # La rentabilidad sobre ventas (margen bruto en porcentaje)
        rentabilidad = (total_margen / total_ventas *
                        100) if total_ventas > 0 else 0

        # Flujo de efectivo real
        flujo_efectivo = ingresos - egresos

        # Margen de contribución real (basado en el margen calculado en ventas)
        margen_contribucion = (
            total_margen / total_ventas * 100) if total_ventas > 0 else 0

        # Cálculo para la inclinación de la balanza
        # En lugar de comparar ventas vs compras, usamos el margen
        # Si hay margen positivo, la balanza se inclina hacia ventas
        # Si hay pérdida, se inclina hacia compras
        max_angle = 15  # Reducir ángulo máximo para mejor visualización
        
        if total_compras > 0:
            # Calcular el porcentaje de margen respecto a las compras
            margin_percentage = (total_margen / total_compras) * 100
            # Convertir porcentaje a ángulo (cada 10% = 3 grados)
            # Convertir a float para evitar errores de tipo con Decimal
            margin_float = float(margin_percentage)
            balance_angle = min(
                max_angle, max(-max_angle, margin_float * 0.3))
        else:
            balance_angle = 0

        # Asegurar que balance_angle es siempre un número válido
        try:
            balance_angle = float(balance_angle)
            # Check for NaN o valores inválidos
            if (not isinstance(balance_angle, (int, float)) or
                    balance_angle != balance_angle):
                balance_angle = 0.0
            # Redondear a 2 decimales para evitar problemas de precisión
            balance_angle = round(balance_angle, 2)
        except (TypeError, ValueError):
            balance_angle = 0.0

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

            month_sales_base = Order.objects.filter(
                type_document='ORD_VENTA',
                date__date__range=[month_start, month_end],
                status__in=['CONFIRMADO', 'FACTURADO']
            ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

            # Obtener el margen real del mes
            month_margin = Order.objects.filter(
                type_document='ORD_VENTA',
                date__date__range=[month_start, month_end],
                status__in=['CONFIRMADO', 'FACTURADO']
            ).aggregate(
                Sum('total_margin'))['total_margin__sum'] or Decimal('0')
            
            # Total de ventas incluye el margen
            month_sales = month_sales_base + month_margin

            monthly_data.append({
                'month': month_start.strftime('%m/%Y'),
                'purchases': float(month_purchases),
                'sales': float(month_sales),
                # Usar margen real en lugar de ventas - compras
                'profit': float(month_margin)
            })

        monthly_data.reverse()  # Ordenar cronológicamente

        # === INDICADORES KPI ===
        kpis = {
            # ROI basado en margen real vs inversión en compras
            'roi': (total_margen / total_compras * 100
                    ) if total_compras > 0 else 0,
            'ticket_promedio_venta': (
                total_ventas / count_ventas) if count_ventas > 0 else 0,
            'ticket_promedio_compra': (
                total_compras / count_compras) if count_compras > 0 else 0,
            # Ratio de eficiencia: cuánto se vende por cada peso comprado
            'ratio_ventas_compras': (
                total_ventas / total_compras) if total_compras > 0 else 0,
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
            'balance_angle': balance_angle,  # Ángulo para inclinar la balanza
            'kpis': kpis,

            # Datos temporales - convertir a JSON string
            'monthly_data_json': json.dumps(monthly_data),
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        # Manejar exportación a Excel/PDF si es necesario
        return JsonResponse({
            "message": "Export functionality to be implemented"})
