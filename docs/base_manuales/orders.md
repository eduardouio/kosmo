# Manual del Módulo de Órdenes

![Logo Kosmo Flowers]

## Introducción

El módulo de Órdenes de Kosmo Flowers permite gestionar todo el ciclo de compra y venta de productos florales. Este sistema facilita la creación, seguimiento y procesamiento de órdenes tanto para clientes como para proveedores, manteniendo un control completo del flujo comercial.

Este manual detalla las funcionalidades del módulo y proporciona instrucciones paso a paso para su uso eficiente.

## Índice

1. [Conceptos Básicos](#1-conceptos-básicos)
2. [Órdenes de Cliente](#2-órdenes-de-cliente)
3. [Órdenes de Proveedor](#3-órdenes-de-proveedor)
4. [Detalle de Órdenes](#4-detalle-de-órdenes)
5. [Aprobación de Órdenes](#5-aprobación-de-órdenes)
6. [Cancelación de Órdenes](#6-cancelación-de-órdenes)
7. [Creación de Facturas](#7-creación-de-facturas)
8. [Estados de las Órdenes](#8-estados-de-las-órdenes)
9. [Indicadores y Estadísticas](#9-indicadores-y-estadísticas)
10. [Atajos y Consejos Avanzados](#10-atajos-y-consejos-avanzados)

---

## 1. Conceptos Básicos

El sistema de órdenes de Kosmo Flowers maneja dos tipos principales de documentos:

- **Órdenes de Cliente (Venta)**: Registran las solicitudes de compra realizadas por clientes.
- **Órdenes de Proveedor (Compra)**: Documentan las adquisiciones realizadas a proveedores para cumplir con las órdenes de clientes.

Cada orden tiene un ciclo de vida definido a través de diferentes estados:

| Estado | Descripción | Acciones permitidas |
|--------|-------------|---------------------|
| PENDIENTE | Orden recién creada | Editar, Confirmar, Cancelar |
| MODIFICADO | Orden que ha sufrido cambios | Editar, Confirmar, Cancelar |
| CONFIRMADO | Orden aprobada para procesamiento | Facturar, Cancelar |
| FACTURADO | Orden con factura asociada | Solo visualización |
| CANCELADO | Orden anulada | Solo visualización |
| PROMESA | Orden de entrega futura | Editar, Confirmar, Cancelar |

## 2. Órdenes de Cliente

**Ruta de acceso:** Menú Principal > Trade > Customer Orders

![Lista de Órdenes de Cliente]

Esta funcionalidad le permite:
- **Visualizar** todas las órdenes de venta a clientes
- **Crear** nuevas órdenes de venta
- **Acceder** al detalle de cada orden
- **Realizar seguimiento** del estado de cada orden

### Información principal:

En la lista de órdenes de cliente se muestra:
- **Número de orden**: Identificador único (Serie-Consecutivo)
- **Cliente**: Nombre del cliente que realizó la orden
- **Fecha**: Fecha de creación
- **Fecha de entrega**: Fecha programada para la entrega
- **Estado**: Estado actual de la orden
- **Total**: Valor total de la orden
- **Productos**: Resumen de productos solicitados
- **Acciones**: Botones para gestionar la orden

### Indicadores de órdenes de cliente:

En la parte superior de la lista se muestran indicadores relevantes:
- **Por confirmar**: Valor en dólares de órdenes pendientes de confirmación
- **Ventas facturadas**: Cantidad de órdenes que ya tienen factura
- **Tallos confirmados**: Total de tallos en órdenes confirmadas
- **Tallos facturados**: Total de tallos en órdenes facturadas
- **Ventas del mes**: Valor total de órdenes creadas en el mes actual
- **Facturado del mes**: Valor total de órdenes facturadas en el mes actual

### Crear una orden de cliente:

1. Desde la vista de Stock, seleccione los productos deseados
2. Haga clic en "Crear Pedido"
3. Seleccione el cliente destinatario
4. Ajuste cantidades y precios si es necesario
5. Revise el resumen del pedido
6. Haga clic en "Confirmar Pedido"

## 3. Órdenes de Proveedor

**Ruta de acceso:** Menú Principal > Trade > Supplier Orders

![Lista de Órdenes de Proveedor]

Esta funcionalidad le permite:
- **Visualizar** todas las órdenes de compra a proveedores
- **Acceder** al detalle de cada orden
- **Realizar seguimiento** del estado de cada orden
- **Verificar** la relación con órdenes de cliente

### Información principal:

En la lista de órdenes de proveedor se muestra:
- **Número de orden**: Identificador único (Serie-Consecutivo)
- **Proveedor**: Nombre del proveedor
- **Orden de cliente relacionada**: Número de la orden de venta asociada
- **Fecha**: Fecha de creación
- **Fecha de entrega**: Fecha programada para la recepción
- **Estado**: Estado actual de la orden
- **Total**: Valor total de la compra
- **Productos**: Resumen de productos solicitados
- **Acciones**: Botones para gestionar la orden

### Indicadores de órdenes de proveedor:

En la parte superior de la lista se muestran indicadores relevantes:
- **Por confirmar**: Valor en dólares de órdenes pendientes de confirmación
- **Compras facturadas**: Cantidad de órdenes que ya tienen factura
- **Tallos confirmados**: Total de tallos en órdenes confirmadas
- **Tallos facturados**: Total de tallos en órdenes facturadas
- **Compras del mes**: Valor total de órdenes creadas en el mes actual
- **Facturado del mes**: Valor total de órdenes facturadas en el mes actual

### Creación de órdenes de proveedor:

Las órdenes de proveedor se generan automáticamente al crear una orden de cliente, asignando cada producto al proveedor correspondiente.

## 4. Detalle de Órdenes

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders > [Número de Orden]

![Detalle de Orden]

La vista de detalle muestra información completa sobre una orden específica:

### Información general:

- **Número de orden**: Identificador único
- **Cliente/Proveedor**: Entidad relacionada con la orden
- **Fecha de creación**: Cuando se generó la orden
- **Fecha de entrega**: Cuando debe entregarse o recibirse
- **Estado**: Estado actual en el ciclo de vida
- **Referencia**: Número de orden del cliente (PO)

### Detalle de productos:

- **Producto**: Variedad de flor
- **Longitud**: Tamaño del tallo en centímetros
- **Cantidad**: Número de tallos o ramos
- **Precio unitario**: Valor por tallo o ramo
- **Margen**: Ganancia aplicada (solo para órdenes de venta)
- **Subtotal**: Valor de la línea

### Totales y resumen:

- **Total de cajas**: Desglose por tipo (HB, QB, EB, FB)
- **Total de tallos**: Suma de todos los tallos en la orden
- **Subtotal**: Suma de todos los productos
- **Margen total**: Suma de los márgenes (solo para órdenes de venta)
- **Total**: Valor final de la orden

### Acciones disponibles:

Las acciones varían según el estado de la orden:
- **Confirmar**: Aprueba la orden para procesamiento
- **Editar**: Permite modificar cantidades y productos
- **Cancelar**: Anula la orden
- **Crear Factura**: Genera una factura a partir de la orden
- **Imprimir**: Genera un PDF con el detalle de la orden

## 5. Aprobación de Órdenes

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders > [Número de Orden] > Confirmar

![Aprobación de Orden]

El proceso de aprobación valida la orden y la marca como lista para procesamiento.

### Aprobación de orden de cliente:

1. Abra el detalle de la orden que desea aprobar
2. Verifique que todos los datos sean correctos
3. Haga clic en el botón "Confirmar"
4. El sistema automáticamente:
   - Cambia el estado de la orden a "CONFIRMADO"
   - Confirma todas las órdenes de proveedor asociadas

### Aprobación de orden de proveedor:

1. Abra el detalle de la orden que desea aprobar
2. Verifique que todos los datos sean correctos
3. Haga clic en el botón "Confirmar"
4. El sistema:
   - Cambia el estado de la orden a "CONFIRMADO"
   - Verifica si todas las órdenes de proveedor relacionadas con la orden de cliente están confirmadas
   - Si todas están confirmadas, confirma también la orden de cliente asociada

**Nota:** Una orden solo puede ser aprobada si está en estado "PENDIENTE", "MODIFICADO" o "PROMESA".

## 6. Cancelación de Órdenes

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders > [Número de Orden] > Cancelar

![Cancelación de Orden]

La cancelación anula una orden y la marca como no procesable.

### Cancelación de orden de cliente:

1. Abra el detalle de la orden que desea cancelar
2. Haga clic en el botón "Cancelar"
3. Confirme la acción cuando se le solicite
4. El sistema automáticamente:
   - Cambia el estado de la orden a "CANCELADO"
   - Cancela todas las órdenes de proveedor asociadas

### Cancelación de orden de proveedor:

1. Abra el detalle de la orden que desea cancelar
2. Haga clic en el botón "Cancelar"
3. Confirme la acción cuando se le solicite
4. El sistema:
   - Cambia el estado de la orden a "CANCELADO"
   - Actualiza la orden de cliente asociada, eliminando los productos de este proveedor
   - Recalcula los totales de la orden de cliente

**Limitaciones:** No se pueden cancelar órdenes que ya estén en estado "FACTURADO" o "CANCELADO".

## 7. Creación de Facturas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders > [Número de Orden] > Crear Factura

![Creación de Factura]

Esta funcionalidad permite generar facturas a partir de órdenes confirmadas.

### Pasos para crear una factura:

1. Abra el detalle de la orden que desea facturar
2. Verifique que la orden esté en estado "CONFIRMADO"
3. Haga clic en el botón "Crear Factura"
4. Complete la información adicional requerida:
   - Número de factura del cliente/proveedor
   - Fecha de emisión
   - Términos de pago
5. Haga clic en "Generar Factura"

El sistema automáticamente:
- Crea un registro de factura asociado a la orden
- Cambia el estado de la orden a "FACTURADO"
- Actualiza los indicadores de facturación

## 8. Estados de las Órdenes

Las órdenes en Kosmo Flowers siguen un ciclo de vida definido a través de diferentes estados:

### PENDIENTE
- **Descripción**: Estado inicial de una orden recién creada.
- **Acciones permitidas**: Editar, Confirmar, Cancelar.
- **Transiciones posibles**: → CONFIRMADO, → MODIFICADO, → CANCELADO.

### MODIFICADO
- **Descripción**: Estado de una orden que ha sufrido cambios después de su creación.
- **Acciones permitidas**: Editar, Confirmar, Cancelar.
- **Transiciones posibles**: → CONFIRMADO, → CANCELADO.

### CONFIRMADO
- **Descripción**: Estado de una orden aprobada y lista para procesamiento.
- **Acciones permitidas**: Facturar, Cancelar.
- **Transiciones posibles**: → FACTURADO, → CANCELADO.

### FACTURADO
- **Descripción**: Estado de una orden que ya tiene una factura asociada.
- **Acciones permitidas**: Solo visualización.
- **Transiciones posibles**: Ninguna.

### CANCELADO
- **Descripción**: Estado de una orden anulada que no será procesada.
- **Acciones permitidas**: Solo visualización.
- **Transiciones posibles**: Ninguna.

### PROMESA
- **Descripción**: Estado especial para órdenes de entrega futura.
- **Acciones permitidas**: Editar, Confirmar, Cancelar.
- **Transiciones posibles**: → CONFIRMADO, → MODIFICADO, → CANCELADO.

## 9. Indicadores y Estadísticas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders (panel superior)

![Indicadores y Estadísticas]

El sistema proporciona indicadores clave para el seguimiento de operaciones:

### Indicadores de órdenes de cliente:

- **Por confirmar**: Valor en dólares de órdenes pendientes de confirmación.
- **Ventas facturadas**: Cantidad de órdenes que ya tienen factura.
- **Tallos confirmados**: Total de tallos en órdenes confirmadas.
- **Tallos facturados**: Total de tallos en órdenes facturadas.
- **Ventas del mes**: Valor total de órdenes creadas en el mes actual.
- **Facturado del mes**: Valor total de órdenes facturadas en el mes actual.

### Indicadores de órdenes de proveedor:

- **Por confirmar**: Valor en dólares de órdenes pendientes de confirmación.
- **Compras facturadas**: Cantidad de órdenes que ya tienen factura.
- **Tallos confirmados**: Total de tallos en órdenes confirmadas.
- **Tallos facturados**: Total de tallos en órdenes facturadas.
- **Compras del mes**: Valor total de órdenes creadas en el mes actual.
- **Facturado del mes**: Valor total de órdenes facturadas en el mes actual.

Estos indicadores se actualizan en tiempo real y proporcionan una visión general del estado del negocio.

## 10. Atajos y Consejos Avanzados

- **Flujo eficiente**: Cree órdenes de cliente desde la vista de Stock para garantizar disponibilidad real.
- **Aprobación en lote**: Utilice la función de aprobación en lote para confirmar múltiples órdenes simultáneamente.
- **Impresión de órdenes**: Genere PDFs para compartir con clientes o proveedores.
- **Filtrado avanzado**: Utilice las opciones de filtrado por fecha, estado o cliente/proveedor para localizar órdenes específicas.
- **Verificación de relaciones**: Desde una orden de cliente, verifique todas sus órdenes de proveedor asociadas.
- **Actualización periódica**: Revise regularmente las órdenes pendientes de confirmación para evitar retrasos.
- **Reconciliación de órdenes**: Compare órdenes de cliente con sus correspondientes órdenes de proveedor para garantizar coherencia.

### Mensajes del sistema

Durante la operación del módulo de Órdenes, el sistema puede mostrar diversos mensajes informativos o de error:

| Mensaje | Significado | Acción recomendada |
|---------|-------------|-------------------|
| "Orden confirmada exitosamente" | La orden ha sido aprobada | Proceda a la siguiente fase (facturación) |
| "La orden no puede ser confirmada" | Estado actual no permite confirmación | Verifique el estado actual de la orden |
| "Orden cancelada exitosamente" | La orden ha sido anulada | Ninguna acción requerida |
| "La orden no se puede cancelar" | Estado actual no permite cancelación | Verifique si ya está facturada o cancelada |
| "Factura creada exitosamente" | Se ha generado una factura | Verifique los detalles de la factura |
| "Error al crear factura" | Problemas al generar la factura | Revise los datos de la orden |

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
