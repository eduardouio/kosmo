-- ================================================================
-- VALIDACIÓN DEL REPORTE DE COMPRAS - FACTURAS
-- ================================================================

-- -----------------------------------------------------------------
-- 1. FACTURAS DE COMPRA - Listado básico
-- -----------------------------------------------------------------
SELECT
    inv.id,
    inv.serie,
    inv.consecutive,
    inv.num_invoice,
    inv.date,
    prt.name AS proveedor,
    prt.business_tax_id,
    inv.status,
    inv.total_price AS total_sin_margen,
    inv.total_margin -- Este debe ser ignorado en compras
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND prt.type_partner = 'PROVEEDOR'
ORDER BY inv.date DESC;

-- -----------------------------------------------------------------
-- 2. RESUMEN POR ESTADO DE FACTURAS DE COMPRA
-- -----------------------------------------------------------------
SELECT 
    inv.status,
    COUNT(*) AS cantidad_facturas,
    SUM(inv.total_price) AS total_precio -- Solo precio, sin margen
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY inv.status
ORDER BY inv.status;

-- -----------------------------------------------------------------
-- 3. TOP 10 PROVEEDORES POR MONTO (FACTURAS DE COMPRA)
-- -----------------------------------------------------------------
SELECT 
    prt.name AS proveedor,
    prt.business_tax_id,
    COUNT(inv.id) AS cantidad_facturas,
    SUM(inv.total_price) AS total_compras -- Solo precio, sin margen
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND prt.type_partner = 'PROVEEDOR'
GROUP BY prt.id, prt.name, prt.business_tax_id
ORDER BY total_compras DESC
LIMIT 10;

-- -----------------------------------------------------------------
-- 4. RESUMEN GENERAL DE COMPRAS
-- -----------------------------------------------------------------
SELECT 
    COUNT(*) AS total_facturas,
    SUM(inv.total_price) AS monto_total_sin_margen,
    AVG(inv.total_price) AS promedio_por_factura,
    MIN(inv.date) AS fecha_primera_factura,
    MAX(inv.date) AS fecha_ultima_factura
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA';

-- -----------------------------------------------------------------
-- 5. FACTURAS DE COMPRA CON DETALLE DE ITEMS (MUESTRA)
-- -----------------------------------------------------------------
SELECT
    inv.id AS factura_id,
    inv.num_invoice,
    inv.serie,
    inv.consecutive,
    prt.name AS proveedor,
    inv.total_price AS total_factura,
    itm.box_model,
    itm.quantity AS cantidad_cajas,
    itm.tot_stem_flower AS total_tallos,
    itm.line_total AS total_linea,
    CONCAT(prd.name, ' ', prd.variety) AS producto
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
INNER JOIN trade_invoiceitems itm ON itm.invoice_id = inv.id
INNER JOIN trade_invoiceboxitems ibx ON ibx.invoice_item_id = itm.id
INNER JOIN products_product prd ON prd.id = ibx.product_id
WHERE inv.type_document = 'FAC_COMPRA'
ORDER BY inv.date DESC, inv.id, itm.id
LIMIT 20; -- Solo mostramos 20 registros como muestra

-- -----------------------------------------------------------------
-- 6. VERIFICACIÓN DE CONSISTENCIA - FACTURAS SIN MARGEN
-- -----------------------------------------------------------------
SELECT
    'Facturas con margen mayor a 0' AS verificacion,
    COUNT(*) AS cantidad
FROM trade_invoice
WHERE type_document = 'FAC_COMPRA'
  AND total_margin > 0

UNION ALL

SELECT
    'Total facturas de compra' AS verificacion,
    COUNT(*) AS cantidad
FROM trade_invoice
WHERE type_document = 'FAC_COMPRA';

-- -----------------------------------------------------------------
-- 7. VALIDACIÓN DE PROVEEDORES ACTIVOS
-- -----------------------------------------------------------------
SELECT 
    prt.name,
    prt.business_tax_id,
    prt.status,
    prt.type_partner,
    COUNT(inv.id) AS facturas_compra
FROM partners_partner prt
LEFT JOIN trade_invoice inv ON inv.partner_id = prt.id 
    AND inv.type_document = 'FAC_COMPRA'
WHERE prt.type_partner = 'PROVEEDOR'
  AND prt.is_active = true
GROUP BY prt.id, prt.name, prt.business_tax_id, prt.status, prt.type_partner
ORDER BY facturas_compra DESC, prt.name;
