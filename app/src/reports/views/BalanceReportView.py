"""
Reporte de Balance Financiero basado en Facturas, Cobros y Pagos.

Este reporte se basa completamente en:
- Facturas de Compra (FAC_COMPRA): Para análisis de gastos/inversiones
- Facturas de Venta (FAC_VENTA): Para análisis de ingresos y márgenes
- Pagos (EGRESO): Para análisis de flujo de efectivo de salida
- Cobros (INGRESO): Para análisis de flujo de efectivo de entrada

No utiliza órdenes (ORD_COMPRA/ORD_VENTA) sino únicamente las facturas
emitidas y los movimientos de efectivo reales.
"""

from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from trade.models import Invoice, Payment
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
        purchase_invoices = Invoice.objects.filter(
            type_document='FAC_COMPRA',
            date__date__range=[date_from, date_to],
            status__in=['PENDIENTE', 'PAGADO'],
            is_active=True
        )

        total_compras = purchase_invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        count_compras = purchase_invoices.count()

        # Compras por proveedor con totales de cajas y tallos
        compras_por_proveedor = purchase_invoices.values(
            'partner__name'
        ).annotate(
            total=Sum('total_price'),
            count=Count('id'),
            total_eb=Sum('eb_total'),
            total_hb=Sum('hb_total'),
            total_qb=Sum('qb_total'),
            total_fb=Sum('fb_total'),
            total_tallos=Sum('tot_stem_flower')
        ).order_by('-total')[:15]
        
        # Calcular FB equivalente para compras
        for proveedor in compras_por_proveedor:
            total_fb = Decimal(str(proveedor['total_fb'] or 0))
            total_hb = Decimal(str(proveedor['total_hb'] or 0))
            total_qb = Decimal(str(proveedor['total_qb'] or 0))
            total_eb = Decimal(str(proveedor['total_eb'] or 0))
            
            fb_equivalente = (total_fb + (total_hb / Decimal('2')) +
                              (total_qb / Decimal('4')) + 
                              (total_eb / Decimal('8')))
            proveedor['fb_equivalente'] = fb_equivalente

        # === ANÁLISIS DE VENTAS ===
        sales_invoices = Invoice.objects.filter(
            type_document='FAC_VENTA',
            date__date__range=[date_from, date_to],
            status__in=['PENDIENTE', 'PAGADO'],
            is_active=True
        )

        # Total de ventas (precio base + margen) y margen real obtenido
        total_price_base = sales_invoices.aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        total_margen = sales_invoices.aggregate(
            Sum('total_margin'))['total_margin__sum'] or Decimal('0')
        # Total de ventas real incluye el margen
        total_ventas = total_price_base + total_margen
        count_ventas = sales_invoices.count()

        # Ventas por cliente con totales de cajas y tallos
        ventas_por_cliente = sales_invoices.values(
            'partner__name'
        ).annotate(
            total=Sum('total_price'),
            margin=Sum('total_margin'),  # Margen real obtenido por cliente
            count=Count('id'),
            total_eb=Sum('eb_total'),
            total_hb=Sum('hb_total'),
            total_qb=Sum('qb_total'),
            total_fb=Sum('fb_total'),
            total_tallos=Sum('tot_stem_flower')
        ).order_by('-total')[:15]
        
        # Calcular FB equivalente para ventas
        for cliente in ventas_por_cliente:
            total_fb = Decimal(str(cliente['total_fb'] or 0))
            total_hb = Decimal(str(cliente['total_hb'] or 0))
            total_qb = Decimal(str(cliente['total_qb'] or 0))
            total_eb = Decimal(str(cliente['total_eb'] or 0))
            
            fb_equivalente = (total_fb + (total_hb / Decimal('2')) +
                              (total_qb / Decimal('4')) +
                              (total_eb / Decimal('8')))
            cliente['fb_equivalente'] = fb_equivalente

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

        # Detalle de ingresos (cobros)
        detalle_ingresos = payments.filter(
            type_transaction='INGRESO'
        ).values(
            'payment_number', 'date', 'amount', 'method'
        ).order_by('-date')[:10]

        # Detalle de egresos (pagos)
        detalle_egresos = payments.filter(
            type_transaction='EGRESO'
        ).values(
            'payment_number', 'date', 'amount', 'method'
        ).order_by('-date')[:10]

        # === ANÁLISIS DE FACTURAS Y SU ESTADO DE PAGO ===
        # Facturas de venta pagadas vs pendientes
        facturas_venta_pagadas = sales_invoices.filter(
            status='PAGADO').count()
        facturas_venta_pendientes = sales_invoices.filter(
            status='PENDIENTE').count()
        
        # Facturas de compra pagadas vs pendientes
        facturas_compra_pagadas = purchase_invoices.filter(
            status='PAGADO').count()
        facturas_compra_pendientes = purchase_invoices.filter(
            status='PENDIENTE').count()
        
        # Montos de facturas por estado
        monto_ventas_pagadas = sales_invoices.filter(
            status='PAGADO').aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        monto_ventas_pendientes = sales_invoices.filter(
            status='PENDIENTE').aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        
        monto_compras_pagadas = purchase_invoices.filter(
            status='PAGADO').aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')
        monto_compras_pendientes = purchase_invoices.filter(
            status='PENDIENTE').aggregate(
            Sum('total_price'))['total_price__sum'] or Decimal('0')

        # Margen de facturas pagadas
        margen_ventas_pagadas = sales_invoices.filter(
            status='PAGADO').aggregate(
            Sum('total_margin'))['total_margin__sum'] or Decimal('0')
        margen_ventas_pendientes = sales_invoices.filter(
            status='PENDIENTE').aggregate(
            Sum('total_margin'))['total_margin__sum'] or Decimal('0')

        # === CÁLCULOS DE BALANCE ===
        # La utilidad bruta es el margen real obtenido en las ventas
        utilidad_bruta = total_margen

        # La rentabilidad sobre ventas (margen bruto en porcentaje)
        rentabilidad = (total_margen / total_ventas *
                        100) if total_ventas > 0 else 0

        # Flujo de efectivo real
        flujo_efectivo = ingresos - egresos

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

            month_purchases = Invoice.objects.filter(
                type_document='FAC_COMPRA',
                date__date__range=[month_start, month_end],
                status__in=['PENDIENTE', 'PAGADO'],
                is_active=True
            ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

            month_sales_base = Invoice.objects.filter(
                type_document='FAC_VENTA',
                date__date__range=[month_start, month_end],
                status__in=['PENDIENTE', 'PAGADO'],
                is_active=True
            ).aggregate(Sum('total_price'))['total_price__sum'] or Decimal('0')

            # Obtener el margen real del mes
            month_margin = Invoice.objects.filter(
                type_document='FAC_VENTA',
                date__date__range=[month_start, month_end],
                status__in=['PENDIENTE', 'PAGADO'],
                is_active=True
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
            # KPIs de facturas
            'porcentaje_facturas_venta_pagadas': (
                facturas_venta_pagadas / count_ventas * 100
            ) if count_ventas > 0 else 0,
            'porcentaje_facturas_compra_pagadas': (
                facturas_compra_pagadas / count_compras * 100
            ) if count_compras > 0 else 0,
            # Efectividad de cobro
            'efectividad_cobro': (
                monto_ventas_pagadas / total_ventas * 100
            ) if total_ventas > 0 else 0,
            # Diferencia entre flujo real y flujo teórico
            'diferencia_flujo_teorico': (
                flujo_efectivo - (total_ventas - total_compras)
            ),
        }

        context = {
            'title_page': 'Balance Financiero',
            'filters': {
                'date_from': date_from,
                'date_to': date_to,
            },
            # Datos de compras (Facturas)
            'total_compras': total_compras,
            'count_compras': count_compras,
            'compras_por_proveedor': compras_por_proveedor,

            # Datos de ventas (Facturas)
            'total_ventas': total_ventas,
            'total_margen': total_margen,
            'count_ventas': count_ventas,
            'ventas_por_cliente': ventas_por_cliente,

            # Estado de facturas
            'facturas_venta_pagadas': facturas_venta_pagadas,
            'facturas_venta_pendientes': facturas_venta_pendientes,
            'facturas_compra_pagadas': facturas_compra_pagadas,
            'facturas_compra_pendientes': facturas_compra_pendientes,
            'monto_ventas_pagadas': monto_ventas_pagadas,
            'monto_ventas_pendientes': monto_ventas_pendientes,
            'monto_compras_pagadas': monto_compras_pagadas,
            'monto_compras_pendientes': monto_compras_pendientes,
            'margen_ventas_pagadas': margen_ventas_pagadas,
            'margen_ventas_pendientes': margen_ventas_pendientes,

            # Datos de pagos/cobros
            'ingresos': ingresos,
            'egresos': egresos,
            'flujo_efectivo': flujo_efectivo,
            'detalle_ingresos': detalle_ingresos,
            'detalle_egresos': detalle_egresos,

            # Balance y KPIs
            'utilidad_bruta': utilidad_bruta,
            'rentabilidad': rentabilidad,
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
