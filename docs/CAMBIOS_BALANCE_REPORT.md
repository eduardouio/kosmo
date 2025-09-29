# Resumen de Cambios - Reporte de Balance Financiero

## Cambios Principales

### 1. **Migración de Órdenes a Facturas**
- **Antes**: El reporte se basaba en `Order` (ORD_COMPRA/ORD_VENTA)
- **Ahora**: El reporte se basa en `Invoice` (FAC_COMPRA/FAC_VENTA)

### 2. **Nuevas Consultas de Base de Datos**

#### Facturas de Compra:
```python
purchase_invoices = Invoice.objects.filter(
    type_document='FAC_COMPRA',
    date__date__range=[date_from, date_to],
    status__in=['PENDIENTE', 'PAGADO'],
    is_active=True
)
```

#### Facturas de Venta:
```python
sales_invoices = Invoice.objects.filter(
    type_document='FAC_VENTA',
    date__date__range=[date_from, date_to],
    status__in=['PENDIENTE', 'PAGADO'],
    is_active=True
)
```

### 3. **Nuevas Métricas Agregadas**

#### Estado de Facturas:
- `facturas_venta_pagadas`: Cantidad de facturas de venta pagadas
- `facturas_venta_pendientes`: Cantidad de facturas de venta pendientes
- `facturas_compra_pagadas`: Cantidad de facturas de compra pagadas
- `facturas_compra_pendientes`: Cantidad de facturas de compra pendientes

#### Montos por Estado:
- `monto_ventas_pagadas`: Total de facturas de venta pagadas
- `monto_ventas_pendientes`: Total de facturas de venta pendientes
- `monto_compras_pagadas`: Total de facturas de compra pagadas
- `monto_compras_pendientes`: Total de facturas de compra pendientes

#### Márgenes por Estado:
- `margen_ventas_pagadas`: Margen de facturas de venta pagadas
- `margen_ventas_pendientes`: Margen de facturas de venta pendientes

### 4. **Nuevos KPIs**

- **Porcentaje de facturas de venta pagadas**: `(facturas_venta_pagadas / count_ventas) * 100`
- **Porcentaje de facturas de compra pagadas**: `(facturas_compra_pagadas / count_compras) * 100`
- **Efectividad de cobro**: `(monto_ventas_pagadas / total_ventas) * 100`
- **Diferencia flujo teórico vs real**: `flujo_efectivo - (total_ventas - total_compras)`

### 5. **Mejoras en el Template**

#### Nueva sección "Estado de Facturas":
- Visualización del estado de facturas de venta (pagadas vs pendientes)
- Visualización del estado de facturas de compra (pagadas vs pendientes)
- Indicadores visuales con colores (verde para pagadas, amarillo/rojo para pendientes)
- Métricas de efectividad de cobro y porcentaje de pagos al día

### 6. **Documentación**

Se agregó documentación al inicio del archivo explicando que el reporte se basa en:
- Facturas de Compra (FAC_COMPRA): Para análisis de gastos/inversiones
- Facturas de Venta (FAC_VENTA): Para análisis de ingresos y márgenes  
- Pagos (EGRESO): Para análisis de flujo de efectivo de salida
- Cobros (INGRESO): Para análisis de flujo de efectivo de entrada

## Archivos Modificados

1. **`/app/src/reports/views/BalanceReportView.py`**
   - Cambio de imports: `Order` → `Invoice`
   - Nuevas consultas basadas en facturas
   - Nuevas métricas y KPIs
   - Análisis detallado del estado de facturas

2. **`/app/src/templates/reports/balance_report.html`**
   - Nueva sección "Estado de Facturas"
   - Visualización mejorada del estado de pagos
   - Nuevos indicadores KPI

## Beneficios del Cambio

1. **Datos más precisos**: Las facturas representan compromisos reales vs órdenes que pueden cancelarse
2. **Control de cartera**: Visibilidad clara de facturas pagadas vs pendientes
3. **Flujo de efectivo real**: Basado en facturas emitidas y pagos confirmados
4. **Mejor toma de decisiones**: Métricas más confiables para análisis financiero
5. **Trazabilidad**: Seguimiento del estado real de documentos fiscales

## Estado del Proyecto

✅ **Completado**:
- Migración de consultas de Order a Invoice
- Nuevas métricas de estado de facturas
- Nuevos KPIs de efectividad
- Template actualizado con nuevas visualizaciones
- Documentación agregada

🔄 **Para considerar**:
- Pruebas en ambiente de producción
- Validación con datos reales
- Posible exportación de reportes mejorada