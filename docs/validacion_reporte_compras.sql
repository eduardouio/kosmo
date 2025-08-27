-- ================================================================
-- VALIDACIÓN DEL REPORTE DE COMPRAS - FACTURAS (ACTUALIZADO)
-- ================================================================

-- -----------------------------------------------------------------
-- 1. FACTURAS DE COMPRA - Listado con plazo y vencimientos
-- -----------------------------------------------------------------
SELECT
    inv.id,
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
    CASE 
        WHEN inv.due_date IS NULL THEN FALSE
        ELSE inv.due_date::date < CURRENT_DATE
    END AS esta_vencido,
    prt.name AS proveedor,
    prt.business_tax_id,
    inv.status,
    inv.total_price AS total_sin_margen
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND prt.type_partner = 'PROVEEDOR'
ORDER BY inv.date DESC;

-- -----------------------------------------------------------------
-- 2. RESUMEN POR ESTADO DE FACTURAS DE COMPRA (INCLUYE VENCIDOS)
-- -----------------------------------------------------------------
-- Estados definidos en el modelo
SELECT 
    inv.status,
    COUNT(*) AS cantidad_facturas,
    SUM(inv.total_price) AS total_precio
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY inv.status

UNION ALL

-- Estado calculado: VENCIDO
SELECT 
    'VENCIDO' AS status,
    COUNT(*) AS cantidad_facturas,
    SUM(inv.total_price) AS total_precio
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA'
  AND inv.due_date IS NOT NULL
  AND inv.due_date::date < CURRENT_DATE
  AND inv.status = 'PENDIENTE'

ORDER BY status;

-- -----------------------------------------------------------------
-- 3. FACTURAS VENCIDAS DETALLADAS
-- -----------------------------------------------------------------
SELECT
    inv.id,
    inv.num_invoice,
    inv.serie,
    inv.consecutive,
    inv.date,
    inv.due_date,
    CURRENT_DATE - inv.due_date::date AS dias_vencido,
    prt.name AS proveedor,
    inv.total_price AS total_sin_margen,
    inv.status AS estado_original
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND inv.due_date IS NOT NULL
  AND inv.due_date::date < CURRENT_DATE
  AND inv.status = 'PENDIENTE'
ORDER BY dias_vencido DESC;

-- -----------------------------------------------------------------
-- 4. TOP 10 PROVEEDORES POR MONTO (FACTURAS DE COMPRA)
-- -----------------------------------------------------------------
SELECT 
    prt.name AS proveedor,
    prt.business_tax_id,
    COUNT(inv.id) AS cantidad_facturas,
    SUM(inv.total_price) AS total_compras,
    SUM(CASE WHEN inv.due_date IS NOT NULL AND inv.due_date::date < CURRENT_DATE 
             AND inv.status = 'PENDIENTE' THEN 1 ELSE 0 END) AS facturas_vencidas,
    SUM(CASE WHEN inv.due_date IS NOT NULL AND inv.due_date::date < CURRENT_DATE 
             AND inv.status = 'PENDIENTE' THEN inv.total_price ELSE 0 END) AS monto_vencido
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND prt.type_partner = 'PROVEEDOR'
GROUP BY prt.id, prt.name, prt.business_tax_id
ORDER BY total_compras DESC
LIMIT 10;

-- -----------------------------------------------------------------
-- 5. RESUMEN GENERAL DE COMPRAS CON VENCIMIENTOS
-- -----------------------------------------------------------------
SELECT 
    COUNT(*) AS total_facturas,
    SUM(inv.total_price) AS monto_total_sin_margen,
    COUNT(CASE WHEN inv.status = 'PENDIENTE' THEN 1 END) AS pendientes,
    COUNT(CASE WHEN inv.status = 'PAGADO' THEN 1 END) AS pagadas,
    COUNT(CASE WHEN inv.status = 'ANULADO' THEN 1 END) AS anuladas,
    COUNT(CASE WHEN inv.due_date IS NOT NULL AND inv.due_date::date < CURRENT_DATE 
               AND inv.status = 'PENDIENTE' THEN 1 END) AS vencidas,
    SUM(CASE WHEN inv.due_date IS NOT NULL AND inv.due_date::date < CURRENT_DATE 
             AND inv.status = 'PENDIENTE' THEN inv.total_price ELSE 0 END) AS monto_vencido,
    AVG(inv.total_price) AS promedio_por_factura,
    MIN(inv.date) AS fecha_primera_factura,
    MAX(inv.date) AS fecha_ultima_factura
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA';

-- -----------------------------------------------------------------
-- 6. FACTURAS CON PLAZO PRÓXIMO A VENCER (Próximos 7 días)
-- -----------------------------------------------------------------
SELECT
    inv.id,
    inv.num_invoice,
    inv.date,
    inv.due_date,
    inv.due_date::date - CURRENT_DATE AS dias_para_vencimiento,
    prt.name AS proveedor,
    inv.total_price AS total_sin_margen
FROM trade_invoice inv
INNER JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
  AND inv.status = 'PENDIENTE'
  AND inv.due_date IS NOT NULL
  AND inv.due_date::date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY inv.due_date;

-- -----------------------------------------------------------------
-- 7. VALIDACIÓN DE PLAZO DE CRÉDITO POR PROVEEDOR
-- -----------------------------------------------------------------
SELECT 
    prt.name AS proveedor,
    prt.credit_term AS plazo_credito_configurado,
    COUNT(inv.id) AS total_facturas,
    AVG(CASE WHEN inv.due_date IS NOT NULL 
             THEN inv.due_date::date - inv.date::date 
             ELSE NULL END) AS promedio_dias_plazo_real
FROM partners_partner prt
LEFT JOIN trade_invoice inv ON inv.partner_id = prt.id 
    AND inv.type_document = 'FAC_COMPRA'
WHERE prt.type_partner = 'PROVEEDOR'
  AND prt.is_active = true
GROUP BY prt.id, prt.name, prt.credit_term
ORDER BY total_facturas DESC;
