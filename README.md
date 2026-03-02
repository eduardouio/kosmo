# Kosmo Flowers - Sistema Integrado de Gestión

Este proyecto es un sistema integrado desarrollado para **Kosmo Flowers**, una empresa de comercialización de flores al exterior. El sistema está diseñado para automatizar y optimizar los procesos de gestión de inventarios, pedidos, pagos y coordinación con proveedores, mejorando la eficiencia operativa.

## Módulos Principales

1. **Gestión de Pedidos**
   - Registro y seguimiento de pedidos de clientes.
   - Integración con fuentes de datos externas (correo y Excel).
   - Confirmación automática de pedidos.

2. **Inventario**
   - Monitoreo y actualización diaria del inventario.
   - Control de stock en tiempo real por variedad de flor.
   - Administración de detalles como tallo, grosor, color, etc.

3. **Catálogo de Productos**
   - Registro y gestión de variedades de flores.
   - Mantenimiento del catálogo de productos y códigos de exportación.

4. **Pagos y Créditos**
   - Gestión de pagos a proveedores y recepción de pagos de clientes.
   - Control de créditos según términos acordados (30, 45, 60 días).

5. **Reportes y Análisis**
   - Generación de reportes automáticos sobre inventarios, pagos y otros indicadores clave.
   - Herramientas de análisis de fluctuaciones de costos.

## Configuración del Ambiente de Desarrollo

Este proyecto está desarrollado en **Django**, un framework de Python. Sigue estos pasos para configurar el entorno de desarrollo local:

### Prerrequisitos

- Python 3.8+
- Django 4.x
- PostgreSQL (u otro sistema de base de datos compatible)
- Virtualenv (opcional, pero recomendado)

## requerimientos
- Python 3.8+
- Django 3.x/4.x (según la versión que estés utilizando)
- pip (gestor de paquetes de Python)
- (Opcional) Virtualenv o venv para crear un entorno virtual
### instalacion de dependencias
```bash
pip install -r requeriments.txt
```
-- rm db.sqlite3
## eliminar migraciones
-- find . -path "/migrations/.py" -not -name "init.py" -delete

## Instalación y configuración
```bash
./manage.py makemigrations accounts partners products trade
./manage.py migrate
./manage.py sowseed
./manage.py runserver
```

## Instalación y configuración un solo comando
```bash
./manage.py makemigrations accounts partners products trade &&
./manage.py migrate &&
./manage.py sowseed 
```

## cmd windows
```bash
python manage.py makemigrations accounts partners products trade
python manage.py migrate
python manage.py sowseed 
```

## reiniciar servicio
```bash
sudo systemctl daemon-reload &&
sudo systemctl restart kosmo.service &&
sudo systemctl restart nginx.service
```

## cada vez que se cree en entorno nuevo
```bash
python3 -m venv venv 
source venv/bin/activate
pip install -r requeriments.txt
playwright install 
```


## Exportar Datos
```bash
./mananage.py makemigrations export_model orders
```


# Lista de Fincas a Verificar

| **Nombre de la Finca**              | **Verificado** |
|-------------------------------------|----------------|
| Finca Moonlight Flowers             | Si             |
| Finca Santa Clara                   | Si             |
| Finca Yamiteo Flowers               | Si             |
| Finca Rosas Del Campo               | Si             |
| Finca Fairis Garden                 | Si             |
| Finca Florifrut S.A.                | Si             |
| Finca Flores De La Hacienda         | Si             |
| Finca Valent Roses                  | Si             |
| Finca Spring Roses                  | Si             |
| Finca Floraroma SA                  | Si             |
| Finca Kosmo Flowers SA              | Si             |



TODO
<ul>
<li>[x] Dispos se sobreescriben si se traen de nuevo </li>
<li>[x] Al crear una nueva DAE, deshabilitar las anteriores </li>
<li>[x] Procesar con Chat GPT los Stocks </li>
<li>[ ] Implementar catalogo conforme https://greengoldflowers.com/product/nina/ </li>
<li>[ ] Formulario de carga manual
<li>[x] Generar Paginas de Clientes y Proveedores </li>
<li>[x] Rendimineto en la ficha del socio, sacamos el rendimiento del producto </li>
<li>[x] Agregar campos adicionales en el sicio de negocio </li>
<li>[x] Agregar campos de contacto, email de pagos, skype, web </li>
<li>[x] Cambiar la etiqueta de RUC a ID/RUC/TAX ID </li>
<li>[x] Agregar campos para 2 referencias en la ficha de socio de negocio </li>
<li>[ ] Crear un formulario para el alta de los socios de negocio para posterior aprobación conforme el formato </li>
<li>[ ] Incluir en el formulario de alta los terminos y condiciones de Kosmo, politica de credito, politica de perecibilidad de las flores, notas de credito con plazo de 10 dias </li>
<li>[ ] Los vendedores no pueden ver el proveedor de las flores, solo se mostrará Kosmo como proveedor en el stock </li>
<li>[ ] Las ordenes de los vendedores deben ser aprobadas por el administrador </li>
<li>[ ] La pantalla de los vendedores mostrará información de su progreso mensual </li>
<li>[x] Agregar multiples colores por producto en la ficha del catalogo, permitiendo filtrar por color las variedades, ofrecer un color similar en una variedad diferente </li>
<li>[x] Permitir consultas por color en la tabla de stocks, el catalogo de productos </li>
<li>[ ] Incorporar el rendimiento en las tablas de pedido </li>
<li>[x] Asegurar un margen positivo en cada pedido </li>
<li>[x] Campos relevantes para los pedidos: Variedad, Tamaño, Costo, Precio de venta (automatico), Rentabilidad (basada en el catalogo), Tipo de caja </li>
<li>[ ] Cargar facturas de proveedores al sistema </li>
<li>[ ] Formulario para registro en línea del proveedor o cliente debe estar igual que el Excell con macros </li>
</ul>

# cargar imagenes de productos
```sql
UPDATE products_product SET image = 'products/ROSA-VENDELA.jpg' WHERE id = 2;
UPDATE products_product SET image = 'products/ROSA-TIBET.jpg' WHERE id = 3;
UPDATE products_product SET image = 'products/ROSA-PLAYA_BLANCA.jpg' WHERE id = 4;
UPDATE products_product SET image = 'products/ROSA-ESKIMO.jpg' WHERE id = 5;
UPDATE products_product SET image = 'products/ROSA-MONDIAL.jpeg' WHERE id = 6;
UPDATE products_product SET image = 'products/ROSA-COUNTRY_BLUES.jpg' WHERE id = 7;
UPDATE products_product SET image = 'products/ROSA-DEEP_PURPLE.jpg' WHERE id = 8;
UPDATE products_product SET image = 'products/ROSA-MODDY_BLUES.jpg' WHERE id = 9;
UPDATE products_product SET image = 'products/ROSA-OCEAN_SONG.jpg' WHERE id = 10;
UPDATE products_product SET image = 'products/ROSA-BRIGHTON.jpg' WHERE id = 11;
UPDATE products_product SET image = 'products/ROSA-HIGH_EXOTIC.jpg' WHERE id = 12;
UPDATE products_product SET image = 'products/ROSA-STARDUST.jpg' WHERE id = 13;
UPDATE products_product SET image = 'products/ROSA-TARA.jpg' WHERE id = 14;
UPDATE products_product SET image = 'products/ROSA-HIGH_MAGIC.jpg' WHERE id = 15;
UPDATE products_product SET image = 'products/ROSA-FREE_SPIRIT.jpg' WHERE id = 16;
UPDATE products_product SET image = 'products/ROSA-ORANGE_CRUSH.jpg' WHERE id = 17;
UPDATE products_product SET image = 'products/ROSA-NINA.jpg' WHERE id = 18;
UPDATE products_product SET image = 'products/ROSA-NENA.jpg' WHERE id = 19;
UPDATE products_product SET image = 'products/ROSA-HARDROCK.jpg' WHERE id = 20;
UPDATE products_product SET image = 'products/ROSA-FULL_MONTY.jpg' WHERE id = 21;
UPDATE products_product SET image = 'products/ROSA-ASSORTED.jpg' WHERE id = 22;
UPDATE products_product SET image = 'products/ROSA-GOTCHA.jpg' WHERE id = 23;
UPDATE products_product SET image = 'products/ROSA-PINK_FLOYD.jpg' WHERE id = 24;
UPDATE products_product SET image = 'products/ROSA-SWEET_UNIQUE.jpg' WHERE id = 25;
UPDATE products_product SET image = 'products/ROSA-SWEET_AKITO.jpg' WHERE id = 26;
UPDATE products_product SET image = 'products/ROSA-SWEET_ESKIMO.jpg' WHERE id = 27;
UPDATE products_product SET image = 'products/ROSA-PINK_MONDIAL.jpg' WHERE id = 28;
UPDATE products_product SET image = 'products/ROSA-PRICELESS.jpg' WHERE id = 29;
UPDATE products_product SET image = 'products/ROSA-HERMOSA.jpg' WHERE id = 30;
UPDATE products_product SET image = 'products/ROSA-SHIMMER.jpg' WHERE id = 31;
UPDATE products_product SET image = 'products/ROSA-FREEDOM.jpg' WHERE id = 32;
UPDATE products_product SET image = 'products/ROSA-EXPLORER.jpg' WHERE id = 33;
UPDATE products_product SET image = 'products/ROSA-KAHALA.jpg' WHERE id = 34;
UPDATE products_product SET image = 'products/ROSA-SAHARA.jpg' WHERE id = 35;
UPDATE products_product SET image = 'products/ROSA-QUICKSAND.jpg' WHERE id = 36;
UPDATE products_product SET image = 'products/ROSA-SECRET_GARDEN.jpg' WHERE id = 37;
UPDATE products_product SET image = 'products/ROSA-SECRET.jpg' WHERE id = 38;
UPDATE products_product SET image = 'products/ROSA-TYFANNY.jpg' WHERE id = 39;
UPDATE products_product SET image = 'products/ROSA-TOFEE.jpg' WHERE id = 40;
UPDATE products_product SET image = 'products/ROSA-CANDLELIGHT.jpg' WHERE id = 41;
```

```sql
select
inv.id,
inv.num_invoice,
prt.name,
inv.date ,
inv.type_document ,
inv.status ,
invitm.invoice_id ,
oibx.invoice_item_id ,
invitm.quantity ,
invitm.box_model ,
invitm.tot_stem_flower ,
prod.name ,
prod.variety ,
oibx.stem_cost_price ,
oibx.commission ,
oibx.profit_margin ,
oibx.qty_stem_flower ,
oibx.length ,
invitm.tot_stem_flower ,
invitm.line_price ,
invitm.line_commission ,
invitm.line_margin ,
inv.total_pieces ,
inv.comision_seler ,
inv.total_price ,
inv.total_margin 
from trade_invoiceboxitems oibx
left join products_product prod on (prod.id = oibx.product_id)
left join trade_invoiceitems invitm on  (invitm.id = oibx.invoice_item_id)
left join trade_invoice inv on (inv.id = invitm.invoice_id)
left join partners_partner prt on (prt.id = inv.partner_id)
where inv.type_document = 'FAC_VENTA'


```sql
SELECT * FROM trade_order;

SELECT * FROM trade_orderitems WHERE order_id = 10;

-- consulta a detalle de pedidos 
SELECT 
    to4.id AS "OrdId",
    to4.serie || '-' || LPAD(to4.consecutive::TEXT, 6, '0') AS numero,
    to4.status,
    to3.quantity,
    to3.box_model,
    to4.type_document, 
    pp2.name,
    pp.variety,
    to2.qty_stem_flower,
    to2.stem_cost_price,
    to2.profit_margin, 
    to3.id_stock_detail,
    to3.total_bunches,
    to3.line_total,
    to3.line_price,
    to3.line_margin,
    to3.tot_stem_flower,
    to3.line_commission,
    to3.tot_stem_flower,
    to4.total_bunches,
    to4.total_price,
    to4.total_margin,
    to4.total_stem_flower,
    to4.eb_total,
    to4.qb_total,
    to4.hb_total,
    to4.fb_total
FROM trade_orderboxitems to2
LEFT JOIN products_product pp ON (pp.id = to2.product_id)
LEFT JOIN trade_orderitems to3 ON (to3.id = to2.order_item_id)
LEFT JOIN trade_order to4 ON (to4.id = to3.order_id)
LEFT JOIN partners_partner pp2 ON (pp2.id = to4.partner_id);

-- consulta de detalle de facturas 
SELECT 
    i.id AS "InvId",
    i.serie || '-' || LPAD(i.consecutive::TEXT, 6, '0') AS numero,
    i.status,
    i.type_document,
    i.date,
    i.due_date,
    i.total_price,
    i.total_margin,
    i.comision_seler,
    pp.name AS partner_name,
    pp.business_tax_id,
    ii.box_model,
    ii.quantity,
    ii.tot_stem_flower,
    ii.total_bunches,
    ii.line_price,
    ii.line_margin,
    ii.line_total,
    ibi.product_id,
    p.name AS product_name,
    p.variety,
    ibi.*,
    i.tot_stem_flower AS total_stem_flower,
    i.total_bunches AS invoice_total_bunches,
    i.eb_total,
    i.qb_total,
    i.hb_total,
    i.fb_total,
    i.po_number,
    i.awb,
    i.hawb,
    i.dae_export,
    i.cargo_agency,
    i.delivery_date,
    i.weight,
    i.total_price
FROM trade_invoice i
LEFT JOIN partners_partner pp ON (pp.id = i.partner_id)
LEFT JOIN trade_invoiceitems ii ON (ii.invoice_id = i.id)
LEFT JOIN trade_invoiceboxitems ibi ON (ibi.invoice_item_id = ii.id)
LEFT JOIN products_product p ON (p.id = ibi.product_id)
WHERE i.is_active = TRUE
ORDER BY i.id DESC;
 
-- confirmar todos los socios de negocio
UPDATE partners_partner SET is_verified = TRUE WHERE TRUE;
```

Observaciones de Reunion

[] Opcion para modificar la cantidad de tallos en un QB o HB
[] Cancelacion de pedidos

-- promt primaio
Hola amigo!, vamos a hacer cosas buenas, antes de comenzar quiero que no me halages a menos de que me lo merezca si una ide no es buena dimelo eso me ayuda a crecer y mejorar, si tu tienes algo mejor quiero que me lo digas.

``` sql
UPDATE products_product SET is_active = TRUE WHERE TRUE;
UPDATE partners_bank SET is_active = TRUE WHERE TRUE;
UPDATE partners_dae SET is_active = TRUE WHERE TRUE;
UPDATE partners_contact SET is_active = TRUE WHERE TRUE;

-- Script SQL para corregir la secuencia de ID de productos en PostgreSQL
-- Ejecutar en el servidor de producción donde está ocurriendo el error

-- 1. Verificar el ID máximo actual en la tabla de productos
SELECT MAX(id) AS max_id FROM products_product;

-- 2. Verificar el valor actual de la secuencia
SELECT last_value FROM products_product_id_seq;

-- Ejemplo si el MAX(id) es 25:
SELECT setval('products_product_id_seq', 406, false);

-- proveedores 
-- 1. Verificar el ID máximo actual en la tabla de productos
SELECT MAX(id) AS max_id FROM partners_partner;

-- 2. Verificar el valor actual de la secuencia
SELECT last_value FROM partners_partner_id_seq;

-- Ejemplo si el MAX(id) es 25:
SELECT setval('partners_partner_id_seq', 116, false);

-- proveedores 
SELECT MAX(id) AS max_id FROM partners_contact;

-- 2. Verificar el valor actual de la secuencia
SELECT last_value FROM partners_contact_id_seq;

-- Ejemplo si el MAX(id) es 25:
SELECT setval('partners_contact_id_seq', 10, false);

-- procedimiento de vaciado de datos 
SELECT * FROM trade_invoiceboxitems;
DELETE FROM trade_invoiceboxitems WHERE TRUE;
SELECT last_value FROM trade_invoiceboxitems_id_seq;
SELECT setval('trade_invoiceboxitems_id_seq', 1, false);

-- tradeinvoiceitem
SELECT * FROM trade_invoiceitems;
DELETE FROM trade_invoiceitems WHERE TRUE;
SELECT last_value FROM trade_invoiceitems_id_seq;
SELECT setval('trade_invoiceitems_id_seq', 1, false);

SELECT * FROM trade_invoice;
DELETE FROM trade_invoice WHERE TRUE;
SELECT last_value FROM trade_invoice_id_seq;
SELECT setval('trade_invoice_id_seq', 1, false);

-- ordenes

SELECT * FROM trade_orderboxitems;
DELETE FROM trade_orderboxitems WHERE TRUE;
SELECT last_value FROM trade_orderboxitems_id_seq;
SELECT setval('trade_orderboxitems_id_seq', 1, false);

-- tradeinvoiceitem
SELECT * FROM trade_orderitems;
DELETE FROM trade_orderitems WHERE TRUE;
SELECT last_value FROM trade_orderitems_id_seq;
SELECT setval('trade_orderitems_id_seq', 1, false);

SELECT * FROM trade_order;
DELETE FROM trade_order WHERE TRUE;
SELECT last_value FROM trade_order_id_seq;
SELECT setval('trade_order_id_seq', 1, false);

-- historicos

SELECT * FROM trade_historicalinvoiceitems; 
DELETE FROM trade_historicalinvoiceitems WHERE TRUE;
SELECT last_value FROM trade_historicalinvoiceitems_history_id_seq; 
SELECT setval('trade_historicalinvoiceitems_history_id_seq', 1, false);

SELECT * FROM trade_historicalinvoice; 
DELETE FROM trade_historicalinvoice WHERE TRUE;
SELECT last_value FROM trade_historicalinvoice_history_id_seq; 
SELECT setval('trade_historicalinvoice_history_id_seq', 1, false);

-- ordenes

SELECT * FROM trade_historicalorderboxitems; 
DELETE FROM trade_historicalorderboxitems WHERE TRUE;
SELECT last_value FROM trade_historicalorderboxitems_history_id_seq;
SELECT setval('trade_historicalorderboxitems_history_id_seq', 1, false);

SELECT * FROM trade_historicalorderitems;
DELETE FROM trade_historicalorderitems WHERE TRUE;
SELECT last_value FROM trade_historicalorderitems_history_id_seq;
SELECT setval('trade_historicalorderitems_history_id_seq', 1, false);

SELECT * FROM trade_historicalorder;
DELETE FROM trade_historicalorder WHERE TRUE;
SELECT last_value FROM trade_historicalorder_history_id_seq; 
SELECT setval('trade_historicalorder_history_id_seq', 1, false);

-- stock
SELECT * FROM products_boxitems;
DELETE FROM products_boxitems WHERE TRUE;
SELECT last_value FROM products_boxitems_id_seq;
SELECT setval('products_boxitems_id_seq', 1, false);

SELECT * FROM products_stockdetail;
DELETE FROM products_stockdetail WHERE TRUE;
SELECT last_value FROM products_stockdetail_id_seq;
SELECT setval('products_stockdetail_id_seq', 1, false);

SELECT * FROM products_stockday;
DELETE FROM products_stockday WHERE TRUE;
SELECT last_value FROM products_stockday_id_seq;
SELECT setval('products_stockday_id_seq', 1, false);

-- historico
SELECT * FROM products_historicalboxitems; 
DELETE FROM products_historicalboxitems WHERE TRUE;
SELECT last_value FROM products_historicalboxitems_history_id_seq; 
SELECT setval('products_historicalboxitems_history_id_seq', 1, false);

SELECT * FROM products_historicalstockdetail; 
DELETE FROM products_historicalstockdetail WHERE TRUE; 
SELECT last_value FROM products_historicalstockdetail_history_id_seq; 
SELECT setval('products_historicalstockdetail_history_id_seq', 1, false);

SELECT * FROM products_historicalstockday; 
DELETE FROM products_historicalstockday WHERE TRUE;
SELECT last_value FROM products_historicalstockday_history_id_seq; 
SELECT setval('products_historicalstockday_history_id_seq', 1, false);



Dashboard: http://localhost:8000/sellers/

Stocks: http://localhost:8000/sellers/stocks/

Órdenes: http://localhost:8000/sellers/orders/

Nueva Orden: http://localhost:8000/sellers/orders/create/

Facturas: http://localhost:8000/sellers/invoices/

se debe eligirt de la misma finca

no puede hacer pedidos a varias fincas

usar formato de tabla

ventana de comisiones reporte 
nuevio tipo de pago

ekl pago de comisiones
select * from products_stockday ;
delete from products_stockday where true
SELECT last_value FROM products_stockday_id_seq;
SELECT setval('products_stockday_id_seq', 1, false);


-- historico
select * from products_historicalboxitems ti ; 
delete from products_historicalboxitems where true;
SELECT last_value FROM products_historicalboxitems_history_id_seq; 
SELECT setval('products_historicalboxitems_history_id_seq', 1, false);

select * from products_historicalstockdetail ti ; 
delete from products_historicalstockdetail where true; 
SELECT last_value FROM products_historicalstockdetail_history_id_seq; 
SELECT setval('products_historicalstockdetail_history_id_seq', 1, false);


select * from products_historicalstockday ; 
delete from products_historicalstockday where true;
SELECT last_value FROM products_historicalstockday_history_id_seq; 
SELECT setval('products_historicalstockday_history_id_seq', 1, false);



Dashboard: http://localhost:8000/sellers/

Stocks: http://localhost:8000/sellers/stocks/

Órdenes: http://localhost:8000/sellers/orders/

Nueva Orden: http://localhost:8000/sellers/orders/create/

Facturas: http://localhost:8000/sellers/invoices/

se debe eligirt de la misma finca

no puede hacer pedidos a varias fincas

usar formato de tabla

ventana de comisiones reporte 
nuevio tipo de pago

ekl pago de comisiones



en el estado de cuenta quitarlo


```sql

--
-- cruce de estados de ordenes de venta y compra ordenes facturas relacionadas
--

select  
	o.type_document "DOCUMENTO" ,  
	o.id "ID", 
	o.status "ESTADO", 
	t.type_document "DOCUMENTO",
	t.id "ID" , 
	t.status "ESTADO",
	ti.type_document "DOCUMENTO",
	ti.id "ID",
	ti.status "ESTADO",
	ti2.type_document "DOCUMENTO",
	ti2.id "ID",
	ti2.status "ESTADO"
from trade_order o
left join trade_order t on (t .parent_order_id =  o.id)
left join trade_invoice ti on (ti.order_id  = o.id)
left join trade_invoice ti2 on (t.id  = ti2.order_id)
where 
	o.type_document  = 'ORD_VENTA'
and
	o.status != 'PROMESA'
and 

---

# Cotización — Transformación a Aplicación Móvil

**Proyecto:** Kosmo Flowers — Sistema Integrado de Gestión  
**Fecha:** 02 de Marzo de 2026  
**Objetivo:** Adaptar todas las interfaces del sistema (actualmente diseñadas para escritorio) a una experiencia 100% responsiva y optimizada para dispositivos móviles (smartphones y tablets).

---

## Resumen del Proyecto

Kosmo Flowers es un sistema ERP para comercialización de flores compuesto por **3 aplicaciones frontend (Vue.js)** y **8 módulos backend (Django)**. El flujo principal abarca: Stock → Órdenes de Venta/Compra → Facturación → Pagos/Cobros → Notas de Crédito → Reportes.

El sistema actual fue diseñado exclusivamente para uso en computadores de escritorio. La presente cotización cubre el trabajo necesario para transformar **todas las vistas, componentes y reportes** en interfaces responsivas y mobile-friendly.

---

## Alcance del Trabajo

El trabajo incluye:
- Rediseño responsivo de todas las vistas y componentes Vue.js
- Adaptación de tablas de datos a formatos mobile-friendly (cards, acordeones, scroll horizontal)
- Menús de navegación tipo hamburger/drawer para móvil
- Formularios optimizados para entrada táctil
- Modales y popovers adaptados a pantallas pequeñas
- Reportes PDF adaptados para visualización móvil
- Testing en múltiples resoluciones y dispositivos

---

## Desglose por Módulo

### Frontend — Módulo Orders (Principal)

| # | Pantalla / Componente | Descripción | Tiempo Estimado | Costo (USD) |
|---|----------------------|-------------|-----------------|-------------|
| 1 | **HomeView (Dashboard de Stock)** | Tabla principal de disponibilidad (~887 líneas). Edición inline de precios, costos y márgenes. Filtros laterales. Convertir tabla a cards/acordeones en móvil, adaptar sidebar a drawer. | 5 días | $750 |
| 2 | **ImportView (Importación de Stock)** | Asistente de importación con selección de proveedor, pegado de texto y análisis IA. Adaptar wizard a flujo vertical móvil. | 2 días | $300 |
| 3 | **OrdersView (Listado Pedidos Cliente)** | Listado de pedidos con estados y barra lateral. Convertir a vista tipo lista/cards en móvil. | 2 días | $300 |
| 4 | **PurchasesView (Órdenes de Compra)** | DataTables con paginación y búsqueda. Adaptar tabla a formato card responsivo. | 2 días | $300 |
| 5 | **CompleteOrderView (Detalle de Pedido)** | Vista con tabs para orden de venta y órdenes de compra asociadas. Adaptar tabs a navegación vertical móvil. | 3 días | $450 |
| 6 | **SingleSupplierOrderView** | Detalle de orden de compra individual. Adaptar layout a móvil. | 1 día | $150 |
| 7 | **SingleEditOrderView (Editar Orden)** | Formulario tipo factura (~503 líneas). Tabla de productos con líneas dinámicas, totales automáticos. Adaptar a formulario vertical step-by-step. | 4 días | $600 |
| 8 | **SingleOrderView (Nueva Orden)** | Formulario de "Promesa de Venta" con autocomplete y cálculos en tiempo real (~500+ líneas). Rediseño para entrada táctil. | 4 días | $600 |
| 9 | **PaymentCreateView (Registro de Pagos)** | Facturas pendientes con checkboxes, filtros y formulario de pago. Adaptar lista de facturas a cards seleccionables. | 3 días | $450 |
| 10 | **SingleInvoiceView (Crear Factura)** | Formulario de factura con tabla de productos y totales. Adaptar a layout móvil. | 3 días | $450 |
| 11 | **SideBar (Navegación + Filtros)** | Barra lateral con filtros de proveedores, colores, largos y modelos. Convertir a drawer/bottom-sheet móvil. | 2 días | $300 |
| 12 | **OrderPreview (~728 líneas)** | Vista previa completa del pedido con edición de cantidades. Adaptar a scroll vertical con cards. | 3 días | $450 |
| 13 | **SingleOrderCustomer (~1085 líneas)** | Detalle completo de orden con edición, split/merge de cajas, facturación. Componente más complejo. Rediseño completo para móvil. | 5 días | $750 |
| 14 | **SingleOrderSuplier (~518 líneas)** | Detalle de orden de compra a proveedor (lectura + confirmación). Adaptar a móvil. | 2 días | $300 |
| 15 | **Modales (6 componentes)** | ModalProduct, ModalSuplier, ModalEditBox, ModalShareStock, ModalUpdateValues, ModalOrderPreview. Convertir a bottom-sheets/full-screen en móvil. | 3 días | $450 |
| 16 | **Autocompletes (5 componentes)** | Adaptación de dropdowns de autocompletado para entrada táctil y pantallas pequeñas. | 2 días | $300 |
| 17 | **OrderLine + BoxItem (Trade)** | Líneas de pedido editables con cálculos. Rediseñar para entrada vertical en móvil. | 2 días | $300 |
| | | **Subtotal Módulo Orders** | **46 días** | **$7,200** |

---

### Frontend — Módulo Reports

| # | Pantalla / Componente | Descripción | Tiempo Estimado | Costo (USD) |
|---|----------------------|-------------|-----------------|-------------|
| 18 | **Order.vue (Reporte Orden de Compra)** | Template PDF tipo factura con Tailwind CSS. Adaptar layout a formato vertical A4 mobile-friendly. | 1 día | $150 |
| 19 | **Invoice.vue (Reporte Factura)** | Template PDF de factura con datos de carga (MAWB, HAWB, DAE). Adaptar a mobile. | 1 día | $150 |
| 20 | **Payment.vue (Reporte de Pago)** | Componente base de reporte. Adaptar a mobile. | 0.5 días | $75 |
| | | **Subtotal Módulo Reports** | **2.5 días** | **$375** |

---

### Frontend — Módulo Ventas (Storefront)

| # | Pantalla / Componente | Descripción | Tiempo Estimado | Costo (USD) |
|---|----------------------|-------------|-----------------|-------------|
| 21 | **StorFront.vue (Punto de Venta)** | Scaffold vacío. Diseñar e implementar desde cero con enfoque mobile-first. Incluye catálogo de productos, carrito, checkout. | 8 días | $1,200 |
| | | **Subtotal Módulo Ventas** | **8 días** | **$1,200** |

---

### Backend — Vistas Django (Server-Side Rendered)

| # | Módulo | Descripción | Tiempo Estimado | Costo (USD) |
|---|--------|-------------|-----------------|-------------|
| 22 | **Accounts (9 vistas)** | Login, perfil, lista de vendedores, gestión de usuarios. Adaptar templates Django a diseño responsivo. | 3 días | $450 |
| 23 | **Partners (10 vistas)** | CRUD de clientes/proveedores, contactos, bancos, DAEs. Adaptar formularios y tablas a móvil. | 4 días | $600 |
| 24 | **Products (4 vistas)** | CRUD de catálogo de productos. Adaptar a diseño card/grid responsivo. | 2 días | $300 |
| 25 | **Trade — Stock (6 vistas)** | Gestión de stock diario, importación, detalles. Adaptar tablas complejas a móvil. | 3 días | $450 |
| 26 | **Trade — Órdenes (8 vistas)** | Órdenes de venta/compra, aprobación individual y batch. Adaptar flujos de trabajo a móvil. | 4 días | $600 |
| 27 | **Trade — Facturas (4 vistas)** | Creación y gestión de facturas. Adaptar formularios y tablas. | 2 días | $300 |
| 28 | **Trade — Pagos/Cobros (6 vistas)** | Registro de pagos y cobros, anulación. Adaptar a móvil con UX de selección táctil. | 3 días | $450 |
| 29 | **Trade — Notas de Crédito (2 vistas)** | Creación y gestión de notas de crédito. Adaptar a móvil. | 1 día | $150 |
| 30 | **Sellers (6 vistas)** | Dashboard vendedor, stock, órdenes, factura. Adaptar a experiencia móvil dedicada para vendedores en campo. | 3 días | $450 |
| | | **Subtotal Backend Views** | **25 días** | **$3,750** |

---

### Backend — Reportes PDF (Django)

| # | Módulo | Descripción | Tiempo Estimado | Costo (USD) |
|---|--------|-------------|-----------------|-------------|
| 31 | **Reportes PDF (14 templates)** | Orden cliente/proveedor, factura, balance, pago, cobro, nota de crédito. Adaptar templates HTML/PDF a formatos legibles en móvil. | 5 días | $750 |
| 32 | **Reportes Tabulares (8 vistas)** | Compras, Ventas, Balance, Estado de cuenta. Tablas complejas con agregaciones. Adaptar a formato card/acordeón en móvil. | 4 días | $600 |
| | | **Subtotal Reportes** | **9 días** | **$1,350** |

---

### Tareas Transversales

| # | Tarea | Descripción | Tiempo Estimado | Costo (USD) |
|---|-------|-------------|-----------------|-------------|
| 33 | **Framework CSS Responsivo** | Implementar sistema de grillas y breakpoints. Unificar Bootstrap (Orders) y Tailwind (Reports). Media queries globales. | 3 días | $450 |
| 34 | **Navegación Móvil Global** | Diseñar e implementar menú hamburger/drawer, bottom navigation bar, breadcrumbs adaptados. | 2 días | $300 |
| 35 | **Touch & Gestures** | Implementar swipe, pull-to-refresh, long-press y gestos táctiles en componentes interactivos. | 3 días | $450 |
| 36 | **Testing & QA Responsivo** | Pruebas en Chrome DevTools, dispositivos físicos (iOS/Android), múltiples resoluciones. Corrección de bugs visuales. | 5 días | $750 |
| 37 | **Optimización de Performance Móvil** | Lazy loading, compresión de imágenes, reducción de bundle size, service workers para carga offline. | 3 días | $450 |
| | | **Subtotal Transversales** | **16 días** | **$2,400** |

---

## Resumen General de la Cotización

| Módulo | Ítems | Tiempo Estimado | Costo (USD) |
|--------|-------|-----------------|-------------|
| Frontend — Orders (Principal) | 17 | 46 días | $7,200 |
| Frontend — Reports | 3 | 2.5 días | $375 |
| Frontend — Ventas (Storefront) | 1 | 8 días | $1,200 |
| Backend — Vistas Django | 9 | 25 días | $3,750 |
| Backend — Reportes PDF | 2 | 9 días | $1,350 |
| Tareas Transversales | 5 | 16 días | $2,400 |
| **TOTAL** | **37** | **106.5 días** | **$16,275** |

---

## Notas Importantes

1. **Los costos son estimaciones referenciales** y serán ajustados según la revisión del cliente.
2. Los tiempos están calculados para **1 desarrollador dedicado**. Con más recursos se puede reducir el calendario.
3. El estimado de **106.5 días hábiles** equivale aproximadamente a **5 meses** de trabajo.
4. No se incluye la creación de una app nativa (React Native, Flutter, etc.). Esta cotización cubre la **transformación responsiva web** para navegadores móviles.
5. El módulo **Ventas (Storefront)** está en estado scaffold vacío, por lo que su costo refleja un desarrollo nuevo con enfoque mobile-first.
6. Se recomienda abordar el proyecto en **fases**:
   - **Fase 1:** Tareas Transversales + Módulo Orders (lo más usado)
   - **Fase 2:** Backend Views + Reportes
   - **Fase 3:** Módulo Ventas (Storefront)

---

## Estadísticas del Proyecto Actual

| Métrica | Valor |
|---------|-------|
| Líneas de código Python (backend) | ~22,700 |
| Líneas de código Vue.js (frontend) | ~6,450 |
| Modelos Django | 17 |
| Endpoints API REST | ~38 |
| Vistas frontend Vue.js | 12 |
| Componentes Vue.js | 29 |
| Stores Pinia | 8 |
| Vistas backend Django | ~55 |
| Templates de reportes PDF | 14 |
| Apps Django | 8 |
	o.status  != t.status 