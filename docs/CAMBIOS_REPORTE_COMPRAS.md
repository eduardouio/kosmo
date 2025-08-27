# Resumen de Cambios - Reporte de Compras (ACTUALIZADO)

## Problema Identificado
El reporte de compras estaba trabajando con **órdenes** (`Order`) en lugar de **facturas** (`Invoice`), y no estaba ignorando los márgenes como debe ser en las compras. Además faltaba el manejo de facturas vencidas y información de plazos.

## Cambios Realizados

### 1. **PurchaseReportView.py**
- ✅ Cambió de `Order` a `Invoice` con filtro `type_document='FAC_COMPRA'`
- ✅ Removió referencias a márgenes (en compras solo importa el precio de costo)
- ✅ Actualizó filtros para trabajar con proveedores (`type_partner='PROVEEDOR'`)
- ✅ **NUEVO**: Cálculo de facturas vencidas sin modificar el modelo
- ✅ **NUEVO**: Resumen completo de estados incluyendo ceros y "VENCIDO"
- ✅ Cambió nombres de variables: `purchase_orders` → `purchase_invoices`
- ✅ Corrigió referencias a campos de estado del modelo `Invoice`

### 2. **purchase_report.html**
- ✅ Cambió título de "Reporte de Compras" a "Reporte de Facturas de Compra"
- ✅ **NUEVO**: Agregó columnas "Vencimiento" y "Plazo (días)"
- ✅ **NUEVO**: Muestra estado visual de facturas vencidas con badge rojo
- ✅ **NUEVO**: Indicador de días vencidos o días restantes
- ✅ Actualizó iconos y textos en la interfaz
- ✅ Estados específicos de facturas (PAGADO, PENDIENTE, ANULADO, VENCIDO)
- ✅ Agregó clarificación "Total (Sin Margen)" en columnas
- ✅ Cambió variable de loop: `purchase_orders` → `purchase_invoices`

### 3. **Archivos de Validación**
- ✅ Actualizado `validacion_reporte_compras.sql` con:
  - Consultas para facturas vencidas
  - Análisis de plazos de crédito
  - Facturas próximas a vencer
  - Resumen completo con todos los estados

## Nuevas Funcionalidades

### Estados del Reporte
1. **PENDIENTE** → Badge amarillo
2. **PAGADO** → Badge verde  
3. **ANULADO** → Badge rojo
4. **VENCIDO** → Badge rojo (calculado dinámicamente)

### Información de Plazos
- **Columna Vencimiento**: Muestra fecha de vencimiento o "Sin fecha"
- **Columna Plazo**: 
  - Si está vencida: "X días vencido" (badge rojo)
  - Si está pendiente: "X días" (badge azul)
  - Si no tiene fecha: "-"

### Cálculo de Facturas Vencidas
```python
# Se calculan todas las facturas FAC_COMPRA que:
# - Tienen due_date definido
# - due_date < fecha actual
# - status = 'PENDIENTE'
overdue_invoices = Invoice.objects.filter(
    type_document='FAC_COMPRA',
    due_date__isnull=False,
    due_date__date__lt=current_date,
    status__in=['PENDIENTE']
)
```

## Estructura de Datos Actualizada

### Facturas de Compra con Vencimientos
```sql
SELECT 
    inv.serie,
    inv.consecutive, 
    inv.num_invoice,
    inv.date,
    inv.due_date,
    CASE 
        WHEN inv.due_date IS NULL THEN NULL
        WHEN inv.due_date::date < CURRENT_DATE THEN 
            CURRENT_DATE - inv.due_date::date
        ELSE 
            inv.due_date::date - CURRENT_DATE
    END AS dias_plazo,
    prt.name AS proveedor,
    inv.status,
    inv.total_price AS total_sin_margen
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND prt.type_partner = 'PROVEEDOR';
```

### Resumen por Estado (Incluyendo Vencidos)
```sql
-- Estados del modelo
SELECT status, COUNT(*), SUM(total_price)
FROM trade_invoice 
WHERE type_document = 'FAC_COMPRA'
GROUP BY status

UNION ALL

-- Estado calculado: VENCIDO
SELECT 'VENCIDO', COUNT(*), SUM(total_price)
FROM trade_invoice 
WHERE type_document = 'FAC_COMPRA'
  AND due_date::date < CURRENT_DATE
  AND status = 'PENDIENTE';
```

## Beneficios

1. **Datos Correctos**: Ahora el reporte muestra facturas reales en lugar de órdenes
2. **Sin Márgenes**: Las compras solo muestran precios de costo
3. **Control de Vencimientos**: Identifica facturas vencidas automáticamente
4. **Gestión de Plazos**: Muestra información de plazos de crédito
5. **Estados Completos**: Muestra todos los estados, incluso con cero registros
6. **Alertas Visuales**: Badges de colores para identificar rápidamente el estado
7. **Interfaz Mejorada**: Más columnas informativas para mejor gestión

## Validación Recomendada

Ejecutar las consultas en `docs/validacion_reporte_compras.sql` para verificar:
- ✅ Cantidad total de facturas de compra por estado
- ✅ Facturas vencidas y montos  
- ✅ Plazos de crédito por proveedor
- ✅ Facturas próximas a vencer
- ✅ Top proveedores con detalle de vencimientos
- ✅ Consistencia de datos de plazos
