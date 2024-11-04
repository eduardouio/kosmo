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


# cargar imagenes de productos
```sql
UPDATE images SET image = '/media/products/ROSA-VENDELA.jpg' WHERE id = 2;
UPDATE images SET image = '/media/products/ROSA-TIBET.jpg' WHERE id = 3;
UPDATE images SET image = '/media/products/ROSA-PLAYA_BLANCA.jpg' WHERE id = 4;
UPDATE images SET image = '/media/products/ROSA-ESKIMO.jpg' WHERE id = 5;
UPDATE images SET image = '/media/products/ROSA-MONDIAL.jpeg' WHERE id = 6;
UPDATE images SET image = '/media/products/ROSA-COUNTRY_BLUES.jpg' WHERE id = 7;
UPDATE images SET image = '/media/products/ROSA-DEEP_PURPLE.jpg' WHERE id = 8;
UPDATE images SET image = '/media/products/ROSA-MODDY_BLUES.jpg' WHERE id = 9;
UPDATE images SET image = '/media/products/ROSA-OCEAN_SONG.jpg' WHERE id = 10;
UPDATE images SET image = '/media/products/ROSA-BRIGHTON.jpg' WHERE id = 11;
UPDATE images SET image = '/media/products/ROSA-HIGH_EXOTIC.jpg' WHERE id = 12;
UPDATE images SET image = '/media/products/ROSA-STARDUST.jpg' WHERE id = 13;
UPDATE images SET image = '/media/products/ROSA-TARA.jpg' WHERE id = 14;
UPDATE images SET image = '/media/products/ROSA-HIGH_MAGIC.jpg' WHERE id = 15;
UPDATE images SET image = '/media/products/ROSA-FREE_SPIRIT.jpg' WHERE id = 16;
UPDATE images SET image = '/media/products/ROSA-ORANGE_CRUSH.jpg' WHERE id = 17;
UPDATE images SET image = '/media/products/ROSA-NINA.jpg' WHERE id = 18;
UPDATE images SET image = '/media/products/ROSA-NENA.jpg' WHERE id = 19;
UPDATE images SET image = '/media/products/ROSA-HARDROCK.jpg' WHERE id = 20;
UPDATE images SET image = '/media/products/ROSA-FULL_MONTY.jpg' WHERE id = 21;
UPDATE images SET image = '/media/products/ROSA-ASSORTED.jpg' WHERE id = 22;
UPDATE images SET image = '/media/products/ROSA-GOTCHA.jpg' WHERE id = 23;
UPDATE images SET image = '/media/products/ROSA-PINK_FLOYD.jpg' WHERE id = 24;
UPDATE images SET image = '/media/products/ROSA-SWEET_UNIQUE.jpg' WHERE id = 25;
UPDATE images SET image = '/media/products/ROSA-SWEET_AKITO.jpg' WHERE id = 26;
UPDATE images SET image = '/media/products/ROSA-SWEET_ESKIMO.jpg' WHERE id = 27;
UPDATE images SET image = '/media/products/ROSA-PINK_MONDIAL.jpg' WHERE id = 28;
UPDATE images SET image = '/media/products/ROSA-PRICELESS.jpg' WHERE id = 29;
UPDATE images SET image = '/media/products/ROSA-HERMOSA.jpg' WHERE id = 30;
UPDATE images SET image = '/media/products/ROSA-SHIMMER.jpg' WHERE id = 31;
UPDATE images SET image = '/media/products/ROSA-FREEDOM.jpg' WHERE id = 32;
UPDATE images SET image = '/media/products/ROSA-EXPLORER.jpg' WHERE id = 33;
UPDATE images SET image = '/media/products/ROSA-KAHALA.jpg' WHERE id = 34;
UPDATE images SET image = '/media/products/ROSA-SAHARA.jpg' WHERE id = 35;
UPDATE images SET image = '/media/products/ROSA-QUICKSAND.jpg' WHERE id = 36;
UPDATE images SET image = '/media/products/ROSA-SECRET_GARDEN.jpg' WHERE id = 37;
UPDATE images SET image = '/media/products/ROSA-SECRET.jpg' WHERE id = 38;
UPDATE images SET image = '/media/products/ROSA-TYFANNY.jpg' WHERE id = 39;
UPDATE images SET image = '/media/products/ROSA-TOFEE.jpg' WHERE id = 40;
UPDATE images SET image = '/media/products/ROSA-CANDLELIGHT.jpg' WHERE id = 41;
```