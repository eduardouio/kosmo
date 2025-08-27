-- ================================================================
-- VALIDACIÓN DE PEDIDOS (ÓRDENES DE COMPRA Y VENTA)
-- ================================================================

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Detalle con partners
-- -----------------------------------------------------------------
SELECT
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    ord.serie,
    ord.type_document,
    ord.num_order,
    prt.status,
    ord.total_margin,
    ord.total_price
FROM trade_order ord
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.type_document = 'ORD_COMPRA';

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Total general
-- -----------------------------------------------------------------
SELECT SUM(ord.total_price)
FROM trade_order ord
WHERE ord.type_document = 'ORD_COMPRA';

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Resumen por proveedor
-- -----------------------------------------------------------------
SELECT 
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    prt.status,
    SUM(ord.total_price) AS total_compras
FROM trade_order ord
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.type_document = 'ORD_COMPRA'
GROUP BY prt.business_tax_id, prt.name, prt.type_partner, prt.status
ORDER BY total_compras DESC;

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Detalle completo con productos y cajas
-- -----------------------------------------------------------------
SELECT
    prt.name AS partner_name,
    ord.num_order,
    ord.type_document,
    ord.total_price,
    ord.total_margin,
    itm.quantity,
    itm.box_model,
    itm.tot_stem_flower,
    itm.line_price,
    itm.line_margin,
    itm.line_total,
    CONCAT(prd.name, ' ', prd.variety) AS product_name,
    obx.qty_stem_flower,
    obx.stem_cost_price,
    obx.profit_margin
FROM trade_orderboxitems obx
LEFT JOIN products_product prd      ON prd.id = obx.product_id
LEFT JOIN trade_orderitems itm      ON obx.order_item_id = itm.id
LEFT JOIN trade_order ord           ON ord.id = itm.order_id
LEFT JOIN partners_partner prt      ON ord.partner_id = prt.id
WHERE ord.type_document = 'ORD_COMPRA';

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Validación de consistencia entre items y cajas
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    itm.id AS item_id,
    -- Totales del ítem
    itm.tot_stem_flower AS tallos_item,
    itm.line_total      AS total_item,
    itm.line_margin     AS margen_item,
    -- Suma de cajas
    SUM(obx.qty_stem_flower) AS tallos_cajas,
    SUM(obx.qty_stem_flower * obx.stem_cost_price) AS total_cajas,
    SUM(obx.qty_stem_flower * obx.profit_margin)   AS margen_cajas,
    -- Diferencias
    (itm.tot_stem_flower - SUM(obx.qty_stem_flower)) AS diferencia_tallos,
    (itm.line_total - SUM(obx.qty_stem_flower * obx.stem_cost_price)) AS diferencia_total,
    (itm.line_margin - SUM(obx.qty_stem_flower * obx.profit_margin)) AS diferencia_margen
FROM trade_orderboxitems obx
LEFT JOIN trade_orderitems itm ON itm.id = obx.order_item_id
LEFT JOIN trade_order ord      ON ord.id = itm.order_id
WHERE ord.type_document = 'ORD_COMPRA'
GROUP BY ord.id, ord.num_order, itm.id, itm.tot_stem_flower, itm.line_total, itm.line_margin
ORDER BY ord.id, itm.id;

-- -----------------------------------------------------------------
-- ÓRDENES DE COMPRA - Validación de consistencia entre orden e items
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    -- Totales orden
    ord.total_price  AS total_orden,
    ord.total_margin AS margen_orden,
    SUM(itm.tot_stem_flower) AS tallos_items,
    SUM(itm.line_total)      AS total_items,
    SUM(itm.line_margin)     AS margen_items,
    -- Diferencias
    (ord.total_price - SUM(itm.line_total))   AS diferencia_total,
    (ord.total_margin - SUM(itm.line_margin)) AS diferencia_margen
FROM trade_orderitems itm
LEFT JOIN trade_order ord ON ord.id = itm.order_id
WHERE ord.type_document = 'ORD_COMPRA'
GROUP BY ord.id, ord.num_order, ord.total_price, ord.total_margin
ORDER BY ord.id;

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Detalle con partners
-- -----------------------------------------------------------------
SELECT
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    ord.serie,
    ord.type_document,
    ord.num_order,
    prt.status,
    ord.total_margin,
    ord.total_price,
    (ord.total_margin + ord.total_price) AS total_orden
FROM trade_order ord
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.type_document = 'ORD_VENTA';

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Total general
-- -----------------------------------------------------------------
SELECT SUM(ord.total_price + ord.total_margin)
FROM trade_order ord
WHERE ord.type_document = 'ORD_VENTA';

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Resumen por cliente
-- -----------------------------------------------------------------
SELECT 
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    prt.status,
    SUM(ord.total_price + ord.total_margin) AS total_ventas
FROM trade_order ord
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.type_document = 'ORD_VENTA'
GROUP BY prt.business_tax_id, prt.name, prt.type_partner, prt.status
ORDER BY total_ventas DESC;

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Detalle completo con productos y cajas
-- -----------------------------------------------------------------
SELECT
    prt.name AS partner_name,
    ord.num_order,
    ord.type_document,
    ord.total_price,
    ord.total_margin,
    (ord.total_price + ord.total_margin) AS total_orden,
    itm.quantity,
    itm.box_model,
    itm.tot_stem_flower,
    itm.line_price,
    itm.line_margin,
    itm.line_total,
    CONCAT(prd.name, ' ', prd.variety) AS product_name,
    obx.qty_stem_flower,
    obx.stem_cost_price,
    obx.profit_margin
FROM trade_orderboxitems obx
LEFT JOIN products_product prd      ON prd.id = obx.product_id
LEFT JOIN trade_orderitems itm      ON obx.order_item_id = itm.id
LEFT JOIN trade_order ord           ON ord.id = itm.order_id
LEFT JOIN partners_partner prt      ON ord.partner_id = prt.id
WHERE ord.type_document = 'ORD_VENTA';

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Validación de consistencia entre items y cajas
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    itm.id AS item_id,
    -- Totales item
    itm.tot_stem_flower AS tallos_item,
    itm.line_total      AS total_item,
    itm.line_margin     AS margen_item,
    -- Suma de cajas
    SUM(obx.qty_stem_flower) AS tallos_cajas,
    SUM(obx.qty_stem_flower * obx.stem_cost_price) AS total_cajas,
    SUM(obx.qty_stem_flower * obx.profit_margin)   AS margen_cajas,
    -- Diferencias
    (itm.tot_stem_flower - SUM(obx.qty_stem_flower)) AS diferencia_tallos,
    (itm.line_total - SUM(obx.qty_stem_flower * obx.stem_cost_price)) AS diferencia_total,
    (itm.line_margin - SUM(obx.qty_stem_flower * obx.profit_margin)) AS diferencia_margen
FROM trade_orderboxitems obx
LEFT JOIN trade_orderitems itm ON itm.id = obx.order_item_id
LEFT JOIN trade_order ord      ON ord.id = itm.order_id
WHERE ord.type_document = 'ORD_VENTA'
GROUP BY ord.id, ord.num_order, itm.id, itm.tot_stem_flower, itm.line_total, itm.line_margin
ORDER BY ord.id, itm.id;

-- -----------------------------------------------------------------
-- ÓRDENES DE VENTA - Validación de consistencia entre orden e items
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    -- Totales orden
    ord.total_price  AS total_orden,
    ord.total_margin AS margen_orden,
    SUM(itm.tot_stem_flower) AS tallos_items,
    SUM(itm.line_total)      AS total_items,
    SUM(itm.line_margin)     AS margen_items,
    -- Diferencias
    (ord.total_price - SUM(itm.line_total))   AS diferencia_total,
    (ord.total_margin - SUM(itm.line_margin)) AS diferencia_margen
FROM trade_orderitems itm
LEFT JOIN trade_order ord ON ord.id = itm.order_id
WHERE ord.type_document = 'ORD_VENTA'
GROUP BY ord.id, ord.num_order, ord.total_price, ord.total_margin
ORDER BY ord.id;

-- -----------------------------------------------------------------
-- VALIDACIÓN CRUZADA - Órdenes vs Facturas
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document AS tipo_orden,
    ord.is_invoiced,
    ord.id_invoice,
    ord.num_invoice,
    inv.id AS factura_id,
    inv.num_invoice AS num_factura_real,
    inv.type_document AS tipo_factura,
    -- Comparación de totales
    ord.total_price AS precio_orden,
    inv.total_price AS precio_factura,
    ord.total_margin AS margen_orden,
    inv.total_margin AS margen_factura,
    -- Diferencias
    (ord.total_price - inv.total_price) AS diferencia_precio,
    (ord.total_margin - inv.total_margin) AS diferencia_margen
FROM trade_order ord
LEFT JOIN trade_invoice inv ON inv.order_id = ord.id
WHERE ord.is_invoiced = true
ORDER BY ord.id;

-- -----------------------------------------------------------------
-- ÓRDENES PENDIENTES DE FACTURAR
-- -----------------------------------------------------------------
SELECT
    ord.id,
    ord.num_order,
    ord.type_document,
    ord.status,
    prt.name AS partner_name,
    ord.total_price,
    ord.total_margin,
    ord.date,
    ord.delivery_date
FROM trade_order ord
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.is_invoiced = false 
  AND ord.status NOT IN ('CANCELADO', 'PENDIENTE')
ORDER BY ord.date DESC;

-- -----------------------------------------------------------------
-- RESUMEN GENERAL DE ÓRDENES POR ESTADO
-- -----------------------------------------------------------------
SELECT 
    ord.type_document,
    ord.status,
    COUNT(*) AS cantidad_ordenes,
    SUM(ord.total_price) AS total_precio,
    SUM(ord.total_margin) AS total_margen,
    SUM(ord.total_stem_flower) AS total_tallos,
    AVG(ord.total_price) AS promedio_precio
FROM trade_order ord
GROUP BY ord.type_document, ord.status
ORDER BY ord.type_document, ord.status;

-- -----------------------------------------------------------------
-- ÓRDENES CON INCONSISTENCIAS EN TOTALES
-- -----------------------------------------------------------------
SELECT 
    'ORDEN_ITEMS_MISMATCH' AS tipo_error,
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document,
    ord.total_price AS total_orden,
    SUM(itm.line_total) AS total_items,
    (ord.total_price - SUM(itm.line_total)) AS diferencia
FROM trade_order ord
LEFT JOIN trade_orderitems itm ON ord.id = itm.order_id
WHERE itm.is_active = true
GROUP BY ord.id, ord.num_order, ord.type_document, ord.total_price
HAVING ABS(ord.total_price - SUM(itm.line_total)) > 0.01

UNION ALL

SELECT 
    'ITEM_BOXES_MISMATCH' AS tipo_error,
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document,
    itm.line_total AS total_item,
    SUM(obx.qty_stem_flower * obx.stem_cost_price) AS total_cajas,
    (itm.line_total - SUM(obx.qty_stem_flower * obx.stem_cost_price)) AS diferencia
FROM trade_order ord
LEFT JOIN trade_orderitems itm ON ord.id = itm.order_id
LEFT JOIN trade_orderboxitems obx ON itm.id = obx.order_item_id
WHERE itm.is_active = true AND obx.is_active = true
GROUP BY ord.id, ord.num_order, ord.type_document, itm.id, itm.line_total
HAVING ABS(itm.line_total - SUM(obx.qty_stem_flower * obx.stem_cost_price)) > 0.01
ORDER BY orden_id, tipo_error;

-- ================================================================
-- REPORTES DE CRUCE: ÓRDENES vs FACTURAS
-- ================================================================

-- -----------------------------------------------------------------
-- TRAZABILIDAD COMPLETA: Orden → Factura → Items → Cajas
-- -----------------------------------------------------------------
SELECT 
    -- Información de la orden
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document AS tipo_orden,
    ord.status AS estado_orden,
    ord.date AS fecha_orden,
    ord.total_price AS total_orden,
    ord.total_margin AS margen_orden,
    ord.total_stem_flower AS tallos_orden,
    ord.is_invoiced,
    
    -- Información de la factura
    inv.id AS factura_id,
    inv.num_invoice,
    inv.type_document AS tipo_factura,
    inv.status AS estado_factura,
    inv.date AS fecha_factura,
    inv.total_price AS total_factura,
    inv.total_margin AS margen_factura,
    inv.tot_stem_flower AS tallos_factura,
    
    -- Partner
    prt.name AS partner_name,
    prt.type_partner,
    
    -- Diferencias críticas
    (ord.total_price - inv.total_price) AS diferencia_precio,
    (ord.total_margin - inv.total_margin) AS diferencia_margen,
    (ord.total_stem_flower - inv.tot_stem_flower) AS diferencia_tallos,
    
    -- Estado de la validación
    CASE 
        WHEN ord.is_invoiced = true AND inv.id IS NULL THEN 'ERROR: Marcada como facturada pero sin factura'
        WHEN ord.is_invoiced = false AND inv.id IS NOT NULL THEN 'ERROR: Tiene factura pero no marcada'
        WHEN ABS(ord.total_price - inv.total_price) > 0.01 THEN 'ERROR: Diferencia en precios'
        WHEN ABS(ord.total_margin - inv.total_margin) > 0.01 THEN 'ERROR: Diferencia en márgenes'
        WHEN ord.total_stem_flower != inv.tot_stem_flower THEN 'ERROR: Diferencia en tallos'
        WHEN ord.is_invoiced = true AND inv.id IS NOT NULL THEN 'OK: Consistente'
        ELSE 'PENDIENTE: Sin facturar'
    END AS estado_validacion
    
FROM trade_order ord
LEFT JOIN trade_invoice inv ON inv.order_id = ord.id
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
ORDER BY ord.id;

-- -----------------------------------------------------------------
-- ÓRDENES PROBLEMÁTICAS: Inconsistencias críticas
-- -----------------------------------------------------------------
SELECT 
    'ORDEN_SIN_FACTURA' AS problema,
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document,
    ord.status,
    ord.total_price,
    prt.name AS partner_name,
    'Orden marcada como facturada pero sin factura asociada' AS descripcion
FROM trade_order ord
LEFT JOIN trade_invoice inv ON inv.order_id = ord.id
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.is_invoiced = true AND inv.id IS NULL

UNION ALL

SELECT 
    'FACTURA_SIN_MARCAR' AS problema,
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document,
    ord.status,
    ord.total_price,
    prt.name AS partner_name,
    'Tiene factura pero orden no está marcada como facturada' AS descripcion
FROM trade_order ord
INNER JOIN trade_invoice inv ON inv.order_id = ord.id
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ord.is_invoiced = false

UNION ALL

SELECT 
    'DIFERENCIA_TOTALES' AS problema,
    ord.id AS orden_id,
    ord.num_order,
    ord.type_document,
    ord.status,
    ord.total_price,
    prt.name AS partner_name,
    CONCAT('Diferencia en totales: Orden $', ord.total_price, ' vs Factura $', inv.total_price) AS descripcion
FROM trade_order ord
INNER JOIN trade_invoice inv ON inv.order_id = ord.id
LEFT JOIN partners_partner prt ON prt.id = ord.partner_id
WHERE ABS(ord.total_price - inv.total_price) > 0.01

ORDER BY problema, orden_id;

-- -----------------------------------------------------------------
-- FACTURAS HUÉRFANAS: Sin orden asociada
-- -----------------------------------------------------------------
SELECT 
    inv.id AS factura_id,
    inv.num_invoice,
    inv.type_document,
    inv.status,
    inv.total_price,
    inv.total_margin,
    prt.name AS partner_name,
    inv.date AS fecha_factura,
    'Factura sin orden asociada' AS observacion
FROM trade_invoice inv
LEFT JOIN trade_order ord ON ord.id = inv.order_id
LEFT JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE ord.id IS NULL
ORDER BY inv.date DESC;

-- -----------------------------------------------------------------
-- COMPARATIVO DETALLADO: Items de Orden vs Items de Factura
-- -----------------------------------------------------------------
SELECT 
    ord.id AS orden_id,
    ord.num_order,
    inv.id AS factura_id,
    inv.num_invoice,
    
    -- Totales de items de orden
    COUNT(DISTINCT oit.id) AS items_orden,
    SUM(oit.quantity) AS cajas_orden,
    SUM(oit.tot_stem_flower) AS tallos_orden_items,
    SUM(oit.line_total) AS total_orden_items,
    
    -- Totales de items de factura
    COUNT(DISTINCT iit.id) AS items_factura,
    SUM(iit.quantity) AS cajas_factura,
    SUM(iit.tot_stem_flower) AS tallos_factura_items,
    SUM(iit.line_total) AS total_factura_items,
    
    -- Diferencias
    (COUNT(DISTINCT oit.id) - COUNT(DISTINCT iit.id)) AS diferencia_items,
    (SUM(oit.quantity) - SUM(iit.quantity)) AS diferencia_cajas,
    (SUM(oit.tot_stem_flower) - SUM(iit.tot_stem_flower)) AS diferencia_tallos,
    (SUM(oit.line_total) - SUM(iit.line_total)) AS diferencia_totales
    
FROM trade_order ord
INNER JOIN trade_invoice inv ON inv.order_id = ord.id
LEFT JOIN trade_orderitems oit ON oit.order_id = ord.id AND oit.is_active = true
LEFT JOIN trade_invoiceitems iit ON iit.invoice_id = inv.id AND iit.is_active = true
GROUP BY ord.id, ord.num_order, inv.id, inv.num_invoice
ORDER BY ord.id;

-- -----------------------------------------------------------------
-- ANÁLISIS DE PRODUCTOS: Trazabilidad por producto
-- -----------------------------------------------------------------
SELECT 
    prd.name AS producto,
    prd.variety AS variedad,
    
    -- Datos de órdenes
    COUNT(DISTINCT ord.id) AS ordenes_count,
    SUM(CASE WHEN ord.type_document = 'ORD_COMPRA' THEN 1 ELSE 0 END) AS ordenes_compra,
    SUM(CASE WHEN ord.type_document = 'ORD_VENTA' THEN 1 ELSE 0 END) AS ordenes_venta,
    SUM(obx.qty_stem_flower) AS tallos_ordenados,
    SUM(obx.qty_stem_flower * obx.stem_cost_price) AS valor_ordenado,
    
    -- Datos de facturas
    COUNT(DISTINCT inv.id) AS facturas_count,
    SUM(CASE WHEN inv.type_document = 'FAC_COMPRA' THEN 1 ELSE 0 END) AS facturas_compra,
    SUM(CASE WHEN inv.type_document = 'FAC_VENTA' THEN 1 ELSE 0 END) AS facturas_venta,
    SUM(ibx.qty_stem_flower) AS tallos_facturados,
    SUM(ibx.qty_stem_flower * ibx.stem_cost_price) AS valor_facturado,
    
    -- Diferencias
    (SUM(obx.qty_stem_flower) - SUM(ibx.qty_stem_flower)) AS diferencia_tallos,
    (SUM(obx.qty_stem_flower * obx.stem_cost_price) - SUM(ibx.qty_stem_flower * ibx.stem_cost_price)) AS diferencia_valor
    
FROM products_product prd
LEFT JOIN trade_orderboxitems obx ON obx.product_id = prd.id AND obx.is_active = true
LEFT JOIN trade_orderitems oit ON oit.id = obx.order_item_id AND oit.is_active = true
LEFT JOIN trade_order ord ON ord.id = oit.order_id AND ord.is_active = true
LEFT JOIN trade_invoice inv ON inv.order_id = ord.id AND inv.is_active = true
LEFT JOIN trade_invoiceitems iit ON iit.invoice_id = inv.id AND iit.is_active = true
LEFT JOIN trade_invoiceboxitems ibx ON ibx.invoice_item_id = iit.id AND ibx.product_id = prd.id AND ibx.is_active = true
WHERE prd.is_active = true
GROUP BY prd.id, prd.name, prd.variety
HAVING COUNT(DISTINCT ord.id) > 0 OR COUNT(DISTINCT inv.id) > 0
ORDER BY diferencia_valor DESC;

-- -----------------------------------------------------------------
-- RESUMEN EJECUTIVO: Dashboard de control
-- -----------------------------------------------------------------
SELECT 
    'ÓRDENES_TOTALES' AS metrica,
    COUNT(*) AS cantidad,
    SUM(total_price) AS valor_total,
    NULL AS porcentaje
FROM trade_order
WHERE is_active = true

UNION ALL

SELECT 
    'ÓRDENES_FACTURADAS' AS metrica,
    COUNT(*) AS cantidad,
    SUM(total_price) AS valor_total,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trade_order WHERE is_active = true)), 2) AS porcentaje
FROM trade_order
WHERE is_active = true AND is_invoiced = true

UNION ALL

SELECT 
    'ÓRDENES_PENDIENTES' AS metrica,
    COUNT(*) AS cantidad,
    SUM(total_price) AS valor_total,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM trade_order WHERE is_active = true)), 2) AS porcentaje
FROM trade_order
WHERE is_active = true AND is_invoiced = false

UNION ALL

SELECT 
    'FACTURAS_TOTALES' AS metrica,
    COUNT(*) AS cantidad,
    SUM(total_price) AS valor_total,
    NULL AS porcentaje
FROM trade_invoice
WHERE is_active = true

UNION ALL

SELECT 
    'INCONSISTENCIAS_CRÍTICAS' AS metrica,
    COUNT(*) AS cantidad,
    NULL AS valor_total,
    NULL AS porcentaje
FROM (
    SELECT ord.id
    FROM trade_order ord
    LEFT JOIN trade_invoice inv ON inv.order_id = ord.id
    WHERE (ord.is_invoiced = true AND inv.id IS NULL)
       OR (ord.is_invoiced = false AND inv.id IS NOT NULL)
       OR (inv.id IS NOT NULL AND ABS(ord.total_price - inv.total_price) > 0.01)
) inconsistencias

ORDER BY metrica;

-- -----------------------------------------------------------------
-- ALERTAS DE NEGOCIO: Situaciones que requieren atención
-- -----------------------------------------------------------------
SELECT 
    'CRÍTICO' AS nivel,
    'ÓRDENES_SIN_FACTURA_30_DÍAS' AS alerta,
    COUNT(*) AS cantidad,
    CONCAT('Órdenes confirmadas hace más de 30 días sin facturar') AS descripcion
FROM trade_order ord
WHERE ord.is_active = true 
  AND ord.is_invoiced = false
  AND ord.status IN ('CONFIRMADO', 'FACTURADO')
  AND ord.date < CURRENT_DATE - INTERVAL '30 days'

UNION ALL

SELECT 
    'ALTO' AS nivel,
    'DIFERENCIAS_MONETARIAS' AS alerta,
    COUNT(*) AS cantidad,
    'Órdenes con diferencias monetarias vs facturas' AS descripcion
FROM trade_order ord
INNER JOIN trade_invoice inv ON inv.order_id = ord.id
WHERE ABS(ord.total_price - inv.total_price) > 0.01

UNION ALL

SELECT 
    'MEDIO' AS nivel,
    'FACTURAS_HUÉRFANAS' AS alerta,
    COUNT(*) AS cantidad,
    'Facturas sin orden asociada' AS descripcion
FROM trade_invoice inv
LEFT JOIN trade_order ord ON ord.id = inv.order_id
WHERE ord.id IS NULL AND inv.is_active = true

UNION ALL

SELECT 
    'MEDIO' AS nivel,
    'MARCACIÓN_INCORRECTA' AS alerta,
    COUNT(*) AS cantidad,
    'Órdenes con marcación incorrecta de facturación' AS descripcion
FROM trade_order ord
LEFT JOIN trade_invoice inv ON inv.order_id = ord.id
WHERE (ord.is_invoiced = true AND inv.id IS NULL)
   OR (ord.is_invoiced = false AND inv.id IS NOT NULL)

ORDER BY 
    CASE nivel 
        WHEN 'CRÍTICO' THEN 1 
        WHEN 'ALTO' THEN 2 
        WHEN 'MEDIO' THEN 3 
        ELSE 4 
    END,
    cantidad DESC;