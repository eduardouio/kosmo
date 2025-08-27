

-- -----------------------------------------------------------------
SELECT
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    inv.serie,
    inv.type_document,
    inv.num_invoice,
    prt.status,
    inv.total_margin,
    inv.total_price
FROM trade_invoice inv
LEFT JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA';

-- -----------------------------------------------------------------
SELECT SUM(inv.total_price)
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_COMPRA';

-- -----------------------------------------------------------------
SELECT 
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    prt.status,
    SUM(inv.total_price) AS total_compras
FROM trade_invoice inv
LEFT JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY prt.business_tax_id, prt.name, prt.type_partner, prt.status
ORDER BY total_compras DESC;


-- -----------------------------------------------------------------
SELECT
    prt.name AS partner_name,
    inv.num_invoice,
    inv.type_document,
    inv.total_price,
    inv.total_margin,
    itm.quantity,
    itm.box_model,
    itm.tot_stem_flower,
    itm.line_price,
    itm.line_margin,
    itm.line_total,
    CONCAT(prd.name, ' ', prd.variety) AS product_name,
    ibx.qty_stem_flower,
    ibx.stem_cost_price,
    ibx.profit_margin
FROM trade_invoiceboxitems ibx
LEFT JOIN products_product prd      ON prd.id = ibx.product_id
LEFT JOIN trade_invoiceitems itm    ON ibx.invoice_item_id = itm.id
LEFT JOIN trade_invoice inv         ON inv.id = itm.invoice_id
LEFT JOIN partners_partner prt      ON inv.partner_id = prt.id
WHERE inv.type_document = 'FAC_COMPRA';


-- -----------------------------------------------------------------
SELECT 
    inv.id AS factura_id,
    inv.num_invoice,
    itm.id AS item_id,
    -- Totales del ítem
    itm.tot_stem_flower AS tallos_item,
    itm.line_total      AS total_item,
    itm.line_margin     AS margen_item,
    -- Suma de cajas
    SUM(ibx.qty_stem_flower) AS tallos_cajas,
    SUM(ibx.qty_stem_flower * ibx.stem_cost_price) AS total_cajas,
    SUM(ibx.qty_stem_flower * ibx.profit_margin)   AS margen_cajas,
    -- Diferencias
    (itm.tot_stem_flower - SUM(ibx.qty_stem_flower)) AS diferencia_tallos,
    (itm.line_total - SUM(ibx.qty_stem_flower * ibx.stem_cost_price)) AS diferencia_total,
    (itm.line_margin - SUM(ibx.qty_stem_flower * ibx.profit_margin)) AS diferencia_margen
FROM trade_invoiceboxitems ibx
LEFT JOIN trade_invoiceitems itm ON itm.id = ibx.invoice_item_id
LEFT JOIN trade_invoice inv      ON inv.id = itm.invoice_id
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY inv.id, inv.num_invoice, itm.id, itm.tot_stem_flower, itm.line_total, itm.line_margin
ORDER BY inv.id, itm.id;

-- -----------------------------------------------------------------


-- -----------------------------------------------------------------
SELECT
    prt.business_tax_id,
    prt.name,
    prt.type_partner,
    inv.serie,
    inv.type_document,
    inv.num_invoice,
    prt.status,
    inv.total_margin,
    inv.total_price,
    (inv.total_margin + inv.total_price) AS total_invoice
FROM trade_invoice inv
LEFT JOIN partners_partner prt ON prt.id = inv.partner_id
WHERE inv.type_document = 'FAC_VENTA';

-- -----------------------------------------------------------------
SELECT SUM(inv.total_price + inv.total_margin)
FROM trade_invoice inv
WHERE inv.type_document = 'FAC_VENTA';


-- -----------------------------------------------------------------
SELECT
    prt.name AS partner_name,
    inv.num_invoice,
    inv.type_document,
    inv.total_price,
    inv.total_margin,
    (inv.total_price + inv.total_margin) AS total_invoice,
    itm.quantity,
    itm.box_model,
    itm.tot_stem_flower,
    itm.line_price,
    itm.line_margin,
    itm.line_total,
    CONCAT(prd.name, ' ', prd.variety) AS product_name,
    ibx.qty_stem_flower,
    ibx.stem_cost_price,
    ibx.profit_margin
FROM trade_invoiceboxitems ibx
LEFT JOIN products_product prd      ON prd.id = ibx.product_id
LEFT JOIN trade_invoiceitems itm    ON ibx.invoice_item_id = itm.id
LEFT JOIN trade_invoice inv         ON inv.id = itm.invoice_id
LEFT JOIN partners_partner prt      ON inv.partner_id = prt.id
WHERE inv.type_document = 'FAC_VENTA';

-- -----------------------------------------------------------------
SELECT 
    inv.id AS factura_id,
    inv.num_invoice,
    itm.id AS item_id,
    -- Totales item
    itm.tot_stem_flower AS tallos_item,
    itm.line_total      AS total_item,
    itm.line_margin     AS margen_item,
    -- Suma de cajas
    SUM(ibx.qty_stem_flower) AS tallos_cajas,
    SUM(ibx.qty_stem_flower * ibx.stem_cost_price) AS total_cajas,
    SUM(ibx.qty_stem_flower * ibx.profit_margin)   AS margen_cajas,
    -- Diferencias
    (itm.tot_stem_flower - SUM(ibx.qty_stem_flower)) AS diferencia_tallos,
    (itm.line_total - SUM(ibx.qty_stem_flower * ibx.stem_cost_price)) AS diferencia_total,
    (itm.line_margin - SUM(ibx.qty_stem_flower * ibx.profit_margin)) AS diferencia_margen
FROM trade_invoiceboxitems ibx
LEFT JOIN trade_invoiceitems itm ON itm.id = ibx.invoice_item_id
LEFT JOIN trade_invoice inv      ON inv.id = itm.invoice_id
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY inv.id, inv.num_invoice, itm.id, itm.tot_stem_flower, itm.line_total, itm.line_margin
ORDER BY inv.id, itm.id;


-- -----------------------------------------------------------------
SELECT 
    inv.id AS factura_id,
    inv.num_invoice,
    -- Totales factura
    inv.total_price  AS total_factura,
    inv.total_margin AS margen_factura,
    SUM(itm.tot_stem_flower) AS tallos_items,
    SUM(itm.line_total)      AS total_items,
    SUM(itm.line_margin)     AS margen_items,
    -- Diferencias
    (inv.total_price - SUM(itm.line_total))   AS diferencia_total,
    (inv.total_margin - SUM(itm.line_margin)) AS diferencia_margen
FROM trade_invoiceitems itm
LEFT JOIN trade_invoice inv ON inv.id = itm.invoice_id
WHERE inv.type_document = 'FAC_COMPRA'
GROUP BY inv.id, inv.num_invoice, inv.total_price, inv.total_margin
ORDER BY inv.id;
