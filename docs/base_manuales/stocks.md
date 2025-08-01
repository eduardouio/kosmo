# Manual del Módulo de Stocks

![Logo Kosmo Flowers]

## Introducción

El módulo de Stocks de Kosmo Flowers permite gestionar el inventario diario de productos disponibles para la venta. Este sistema facilita el control de disponibilidad, importación de inventarios, creación de pedidos y seguimiento de operaciones comerciales.

Este manual detalla las funcionalidades del módulo y proporciona instrucciones paso a paso para su uso eficiente.

## Índice

1. [Gestión de Stock Diario](#1-gestión-de-stock-diario)
2. [Visualización de Disponibilidad](#2-visualización-de-disponibilidad)
3. [Importación de Inventario](#3-importación-de-inventario)
4. [Gestión de Cajas](#4-gestión-de-cajas)
5. [Creación de Pedidos](#5-creación-de-pedidos)
6. [Compartir Disponibilidad](#6-compartir-disponibilidad)
7. [Modificación Masiva](#7-modificación-masiva)
8. [Filtros y Búsquedas](#8-filtros-y-búsquedas)
9. [Mensajes del Sistema](#9-mensajes-del-sistema)
10. [Atajos y Consejos Avanzados](#10-atajos-y-consejos-avanzados)

---

## 1. Gestión de Stock Diario

**Ruta de acceso:** Menú Principal > Trade > Stock

![Lista de Stock Diario]

Esta funcionalidad le permite:
- **Visualizar** los registros históricos de stock diario
- **Crear** un nuevo registro de stock para el día
- **Acceder** a los detalles de cada día de stock
- **Eliminar** registros antiguos cuando sea necesario

### Crear un nuevo Stock Diario

1. Acceda a "Trade > Stock > Nuevo"
2. El sistema establecerá automáticamente la fecha actual
3. Haga clic en "Guardar"
4. El sistema creará un nuevo registro y lo redireccionará a la pantalla de importación

**Nota:** Al crear un nuevo stock diario, los registros anteriores se desactivan automáticamente para mantener un solo registro activo.

### Detalle de los campos del modelo StockDay:

| Campo | Descripción | Tipo | Obligatorio | Valor predeterminado |
|-------|-------------|------|-------------|----------------------|
| Fecha | Fecha del registro de stock | Fecha | Sí | Fecha actual |
| Activo | Estado del registro | Booleano | Sí | True |

### Eliminar un Stock Diario

1. En la lista de Stock Diario, localice el registro que desea eliminar
2. Haga clic en el botón "Eliminar"
3. Confirme la acción cuando se le solicite

**Advertencia:** No se puede eliminar un stock que tenga dependencias (como pedidos o facturas relacionadas).

## 2. Visualización de Disponibilidad

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock]

![Vista de Disponibilidad]

Esta vista muestra el inventario completo disponible para el día seleccionado, organizado por proveedor y tipo de caja.

### Información principal:

- **Fecha del stock**: Fecha del registro actual
- **Proveedores**: Lista de proveedores con productos disponibles
- **Tipos de caja**: HB (Half Box), QB (Quarter Box), FB (Full Box), EB (Eighth Box)
- **Productos**: Variedades de flores disponibles por proveedor
- **Cantidades**: Número de tallos disponibles por producto

### Interacciones disponibles:

1. **Visualizar detalles de producto**: Haga clic en el nombre del producto
2. **Ver información del proveedor**: Haga clic en el nombre del proveedor
3. **Editar una caja**: Haga clic en el botón "Editar" de una línea específica
4. **Eliminar un producto**: Seleccione y use el botón "Eliminar"

## 3. Importación de Inventario

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock] > Importar

![Importación de Inventario]

Esta funcionalidad permite:
- **Importar** disponibilidad desde texto plano
- **Analizar** automáticamente la información
- **Agregar** nuevos productos al inventario

### Pasos para importar:

1. Seleccione el proveedor al que pertenece el inventario
2. Pegue el texto con la disponibilidad en el campo correspondiente
3. Ajuste el margen de ganancia si es necesario (valor predeterminado: 6%)
4. Seleccione si desea "Agregar al stock existente" o reemplazarlo
5. Haga clic en "Analizar Stock"
6. Revise la información procesada y confirme

### Formato recomendado para el texto:

```
VARIEDAD - COLOR - LONGITUD - CANTIDAD - PRECIO
FREEDOM - ROJO - 50 - 100 - 0.35
MONDIAL - BLANCO - 60 - 200 - 0.40
```

**Nota:** El sistema reconoce diferentes formatos de texto e intenta procesarlos automáticamente.

## 4. Gestión de Cajas

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock] > [Caja específica]

![Edición de Cajas]

Esta funcionalidad permite:
- **Editar** el contenido de las cajas existentes
- **Agregar** nuevos productos a una caja
- **Modificar** cantidades y precios
- **Eliminar** productos de una caja

### Tipos de cajas:

| Código | Nombre | Descripción |
|--------|--------|-------------|
| HB | Half Box | Caja mediana, capacidad aproximada 250-300 tallos |
| QB | Quarter Box | Caja pequeña, capacidad aproximada 100-150 tallos |
| FB | Full Box | Caja grande, capacidad aproximada 500-600 tallos |
| EB | Eighth Box | Caja muy pequeña, capacidad aproximada 50-75 tallos |

### Operaciones con cajas:

1. **Dividir cajas (Split)**: Convierte una caja grande en dos cajas más pequeñas
   - HB → 2 QB
   - QB → 2 EB

2. **Unir cajas (Merge)**: Combina dos cajas pequeñas en una más grande
   - 2 QB → 1 HB
   - 2 EB → 1 QB

### Editar una caja:

1. Seleccione la caja que desea modificar
2. Utilice el formulario para actualizar:
   - Producto (variedad)
   - Longitud
   - Cantidad de tallos
   - Precio por tallo
   - Margen de ganancia
3. Haga clic en "Guardar"

## 5. Creación de Pedidos

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock] > Crear Pedido

![Creación de Pedidos]

Esta funcionalidad permite:
- **Seleccionar** productos del inventario disponible
- **Crear** pedidos para clientes específicos
- **Establecer** cantidades y precios
- **Finalizar** y procesar el pedido

### Pasos para crear un pedido:

1. Seleccione los productos que desea incluir en el pedido
2. Haga clic en "Crear Pedido"
3. Seleccione el cliente destinatario
4. Ajuste las cantidades y precios si es necesario
5. Revise el resumen del pedido:
   - Total de cajas por tipo
   - Total de tallos
   - Costo total
   - Margen de ganancia
6. Haga clic en "Confirmar Pedido"

**Detalle de los campos para pedidos:**

| Campo | Descripción | Tipo | Obligatorio |
|-------|-------------|------|-------------|
| Cliente | Destinatario del pedido | Selección | Sí |
| Fecha | Fecha de creación | Fecha | Sí (automático) |
| Productos | Items seleccionados | Lista | Sí |
| Cantidades | Número de unidades | Número | Sí |
| Precio unitario | Precio por tallo | Decimal | Sí |

## 6. Compartir Disponibilidad

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock] > Compartir

![Compartir Disponibilidad]

Esta funcionalidad permite:
- **Generar** un texto formateado con la disponibilidad
- **Personalizar** la información para clientes específicos
- **Copiar** al portapapeles para compartir por correo o mensajería

### Pasos para compartir disponibilidad:

1. Seleccione los productos que desea incluir
2. Opcionalmente, seleccione un cliente específico para personalizar precios
3. Haga clic en "Generar Texto de Disponibilidad"
4. Utilice el botón "Copiar al Portapapeles"
5. Comparta la información a través de su canal preferido

### Formato de salida personalizable:

```
DISPONIBILIDAD - FECHA: 01/08/2025

FREEDOM - ROJO - 50cm - $0.70 - 100 tallos
MONDIAL - BLANCO - 60cm - $0.85 - 200 tallos

* Precios incluyen transporte
* Disponibilidad sujeta a ventas previas
```

## 7. Modificación Masiva

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock] > Actualizar Valores

![Modificación Masiva]

Esta funcionalidad permite:
- **Modificar** múltiples productos simultáneamente
- **Actualizar** precios o márgenes de ganancia
- **Estandarizar** valores para grupos de productos

### Campos que se pueden modificar masivamente:

1. **Precio por tallo**: Actualiza el precio base de los productos seleccionados
2. **Margen de ganancia**: Modifica el porcentaje de beneficio
3. **Cantidad de tallos**: Ajusta el inventario disponible

### Pasos para modificación masiva:

1. Seleccione los productos que desea modificar
2. Haga clic en "Actualizar Valores"
3. Ingrese los nuevos valores para los campos que desea modificar
4. Confirme la operación
5. Verifique los cambios en la lista principal

## 8. Filtros y Búsquedas

**Ruta de acceso:** Menú Principal > Trade > Stock > [Fecha del Stock]

![Filtros y Búsquedas]

El sistema ofrece múltiples opciones para filtrar y localizar productos específicos:

### Filtros disponibles:

1. **Por proveedor**: Muestra solo productos de un proveedor específico
2. **Por color**: Filtra por el color de las flores
3. **Por longitud**: Selecciona productos según su tamaño
4. **Por tipo de caja**: Filtra por HB, QB, FB o EB
5. **Búsqueda por texto**: Localiza productos por nombre o variedad

### Uso de los filtros:

1. Utilice el panel lateral para activar/desactivar filtros
2. Combine múltiples criterios para búsquedas precisas
3. Use el campo de búsqueda para encontrar texto específico
4. Los resultados se actualizan automáticamente al aplicar filtros

## 9. Mensajes del Sistema

Durante la operación del módulo de Stocks, el sistema puede mostrar diversos mensajes informativos o de error:

| Mensaje | Significado | Acción recomendada |
|---------|-------------|-------------------|
| "Stock Diario Creado Exitosamente" | El registro de stock se ha creado correctamente | Proceda a importar inventario |
| "Stock Diario Eliminado Exitosamente" | Se ha eliminado el registro seleccionado | Ninguna acción requerida |
| "No se puede eliminar el registro. Existen dependencias" | El stock tiene pedidos u otras relaciones | Revise las dependencias antes de intentar eliminar |
| "Inventario importado correctamente" | El texto se ha procesado y agregado al stock | Verifique que todos los productos se hayan importado correctamente |
| "Error al procesar el texto" | Formato no reconocido o datos inconsistentes | Revise el formato del texto importado |
| "Pedido creado exitosamente" | El pedido ha sido procesado | Proceda a revisar el pedido en el módulo correspondiente |

## 10. Atajos y Consejos Avanzados

- **Importación eficiente**: Utilice el formato estándar para agilizar el procesamiento de texto
- **Selección múltiple**: Mantenga presionada la tecla Ctrl/Cmd para seleccionar varios productos no consecutivos
- **Acciones rápidas**: Utilice los botones de acción en la parte superior para operaciones masivas
- **Filtros combinados**: Combine múltiples criterios para búsquedas más precisas
- **Actualización periódica**: Cree un nuevo stock diario al comienzo de cada jornada laboral
- **Respaldo de datos**: Antes de eliminar un stock antiguo, asegúrese de no necesitar su información

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
