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

# Lista de Fincas a Verificar

| **Nombre de la Finca**              | **Verificado** |
|-------------------------------------|----------------|
| Finca Moonlight Flowers             | No             |
| Finca Santa Clara                   | No             |
| Finca Yamiteo Flowers               | No             |
| Finca Rosas Del Campo               | No             |
| Finca Fairis Garden                 | No             |
| Finca Florifrut S.A.                | No             |
| Finca Flores De La Hacienda         | No             |
| Finca Valent Roses                  | No             |
| Finca Spring Roses                  | No             |
| Finca Floraroma SA                  | Sí             |
| Finca Kosmo Flowers SA              | Sí             |



TODO
[] Al crear una nueva DAE, deshabilitar las anteriores
[] Dispos se sobreescriben si se traen de nuevo
[] implementar catalogo conforme https://greengoldflowers.com/product/nina/
[] formulario de carga manual


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