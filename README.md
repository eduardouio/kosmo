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
pip install -r requirements.txt
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
sudo systemctl daemon-reload&&
sudo systemctl restart kosmo.service &&
sudo systemctl restart nginx.service
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

``` sql
select * from trade_order to2  

select * from trade_orderitems to2 where to2.order_id = 10


select 
to4.id 'OrdId', to4.type_document, pp2.name,
to3.id 'OrdItm', to2.id 'IdBox', pp.variety , 
to2.qty_stem_flower, to2.stem_cost_price, to2.profit_margin, 
to3.id_stock_detail, to3.parent_order_item 'Parent' 
from trade_orderboxitems to2
left join products_product pp on (pp.id = to2.product_id)
left join trade_orderitems to3 on (to3.id = to2.order_item_id)
left join trade_order to4 on (to4.id = to3.order_id )
left join partners_partner pp2 on (pp2.id = to4.partner_id)

 
```