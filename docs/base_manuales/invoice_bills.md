# Manual del Módulo de Facturas

![Logo Kosmo Flowers]

## Introducción

El módulo de Facturas de Kosmo Flowers permite gestionar todo el ciclo de facturación relacionado con las operaciones de compra y venta. Este sistema facilita la creación, seguimiento y procesamiento de facturas tanto para clientes como para proveedores, manteniendo un control completo del flujo financiero.

Este manual detalla las funcionalidades del módulo y proporciona instrucciones paso a paso para su uso eficiente.

## Índice

1. [Conceptos Básicos](#1-conceptos-básicos)
2. [Facturas de Cliente](#2-facturas-de-cliente)
3. [Facturas de Proveedor](#3-facturas-de-proveedor)
4. [Detalle de Facturas](#4-detalle-de-facturas)
5. [Creación de Facturas](#5-creación-de-facturas)
6. [Edición de Facturas](#6-edición-de-facturas)
7. [Anulación de Facturas](#7-anulación-de-facturas)
8. [Gestión de Pagos](#8-gestión-de-pagos)
9. [Informes y Exportación](#9-informes-y-exportación)
10. [Atajos y Consejos Avanzados](#10-atajos-y-consejos-avanzados)

---

## 1. Conceptos Básicos

El sistema de facturación de Kosmo Flowers maneja dos tipos principales de documentos:

- **Facturas de Cliente (Venta)**: Documentos emitidos a clientes por la venta de productos.
- **Facturas de Proveedor (Compra)**: Documentos recibidos de proveedores por la adquisición de productos.

Cada factura tiene un ciclo de vida definido a través de diferentes estados:

| Estado | Descripción | Acciones permitidas |
|--------|-------------|---------------------|
| PENDIENTE | Factura emitida pero no pagada | Editar, Anular, Registrar pago |
| PAGADO | Factura completamente pagada | Solo visualización |
| ANULADO | Factura cancelada | Solo visualización |

### Series y Consecutivos

El sistema utiliza series y consecutivos para identificar las facturas:

- **Serie 300**: Facturas de venta a clientes
- **Serie 000**: Facturas de compra a proveedores

Los consecutivos son números secuenciales que se incrementan automáticamente para cada serie.

## 2. Facturas de Cliente

**Ruta de acceso:** Menú Principal > Trade > Customer Invoices

![Lista de Facturas de Cliente]

Esta funcionalidad le permite:
- **Visualizar** todas las facturas emitidas a clientes
- **Acceder** al detalle de cada factura
- **Hacer seguimiento** del estado de pago de cada factura
- **Filtrar y buscar** facturas específicas

### Información principal:

En la lista de facturas de cliente se muestra:
- **Número de factura**: Identificador único (Serie-Consecutivo)
- **Cliente**: Nombre del cliente facturado
- **Orden relacionada**: Número de la orden que generó la factura
- **Fecha de emisión**: Cuando se generó la factura
- **Fecha de vencimiento**: Plazo máximo para pago
- **Estado**: Estado actual de la factura
- **Total**: Valor total de la factura
- **Productos**: Resumen de productos facturados
- **Acciones**: Botones para gestionar la factura

### Indicadores de facturas de cliente:

En la parte superior de la lista se muestran indicadores relevantes:
- **Facturas activas**: Cantidad de facturas pendientes de pago
- **Total por cobrar**: Valor en dólares de facturas pendientes
- **Por cobrar este mes**: Valor pendiente con vencimiento en el mes actual
- **Total cobrado**: Valor total de facturas pagadas
- **Tallos facturados este mes**: Total de tallos en facturas del mes actual

## 3. Facturas de Proveedor

**Ruta de acceso:** Menú Principal > Trade > Supplier Invoices

![Lista de Facturas de Proveedor]

Esta funcionalidad le permite:
- **Visualizar** todas las facturas recibidas de proveedores
- **Acceder** al detalle de cada factura
- **Hacer seguimiento** del estado de pago
- **Registrar** pagos realizados

### Información principal:

En la lista de facturas de proveedor se muestra:
- **Número de factura**: Identificador del proveedor o sistema
- **Proveedor**: Nombre del proveedor
- **Orden relacionada**: Número de la orden de compra
- **Fecha de emisión**: Cuando se recibió la factura
- **Fecha de vencimiento**: Plazo máximo para pago
- **Estado**: Estado actual de la factura
- **Total**: Valor total a pagar
- **Productos**: Resumen de productos facturados
- **Acciones**: Botones para gestionar la factura

### Indicadores de facturas de proveedor:

En la parte superior de la lista se muestran indicadores relevantes:
- **Facturas activas**: Cantidad de facturas pendientes de pago
- **Total por pagar**: Valor en dólares de facturas pendientes
- **Por pagar este mes**: Valor pendiente con vencimiento en el mes actual
- **Total pagado**: Valor total de facturas pagadas
- **Tallos comprados este mes**: Total de tallos en facturas del mes actual

## 4. Detalle de Facturas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Invoices > [Número de Factura]

![Detalle de Factura]

La vista de detalle muestra información completa sobre una factura específica:

### Información general:

- **Número de factura**: Identificador único
- **Cliente/Proveedor**: Entidad relacionada con la factura
- **Fecha de emisión**: Cuando se generó la factura
- **Fecha de vencimiento**: Plazo máximo para pago
- **Estado**: Estado actual en el ciclo de vida
- **Orden relacionada**: Número de la orden que generó la factura

### Información de envío (solo facturas de venta):

- **AWB**: Número de guía aérea principal
- **HAWB**: Número de guía aérea secundaria
- **DAE**: Documento de exportación
- **Agencia de carga**: Empresa transportadora
- **Fecha de entrega**: Cuando se entregaron los productos
- **Peso**: Peso total en kilogramos

### Detalle de productos:

- **Producto**: Variedad de flor
- **Longitud**: Tamaño del tallo en centímetros
- **Cantidad**: Número de tallos o ramos
- **Precio unitario**: Valor por tallo o ramo
- **Margen**: Ganancia aplicada (solo para facturas de venta)
- **Subtotal**: Valor de la línea

### Totales y resumen:

- **Total de cajas**: Desglose por tipo (HB, QB, EB, FB)
- **Total de tallos**: Suma de todos los tallos en la factura
- **Subtotal**: Suma de todos los productos
- **Margen total**: Suma de los márgenes (solo para facturas de venta)
- **Total**: Valor final de la factura

### Información de pago:

- **Estado de pago**: Pendiente, Pagado o Anulado
- **Días para vencimiento**: Tiempo restante para pago (si está pendiente)
- **Días vencidos**: Tiempo transcurrido desde vencimiento (si está vencida)

## 5. Creación de Facturas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Orders > [Número de Orden] > Crear Factura

![Creación de Factura]

Las facturas se generan a partir de órdenes confirmadas:

### Creación de factura de cliente:

1. Acceda al detalle de la orden de venta que desea facturar
2. Verifique que la orden esté en estado "CONFIRMADO"
3. Haga clic en el botón "Crear Factura"
4. El sistema automáticamente:
   - Crea una factura con los datos de la orden
   - Asigna un número consecutivo de serie 300
   - Establece la fecha de vencimiento según el plazo de crédito del cliente
   - Cambia el estado de la orden a "FACTURADO"
   - Genera automáticamente facturas de compra para los proveedores relacionados

### Creación de factura de proveedor:

Las facturas de proveedor se generan automáticamente al crear una factura de cliente. Sin embargo, también se pueden crear manualmente:

1. Acceda al detalle de la orden de compra que desea facturar
2. Verifique que la orden esté en estado "CONFIRMADO"
3. Haga clic en el botón "Crear Factura"
4. El sistema:
   - Crea una factura con los datos de la orden
   - Asigna un número preliminar "SinFact-[Número de Orden]"
   - Establece la fecha de vencimiento según el plazo de crédito del proveedor
   - Cambia el estado de la orden a "FACTURADO"

**Nota:** Después de crear una factura de proveedor manualmente, debe actualizar el número de factura real proporcionado por el proveedor.

## 6. Edición de Facturas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Invoices > [Número de Factura] > Editar

![Edición de Factura]

Después de crear una factura, puede editar cierta información:

### Campos editables en facturas de cliente:

- **Fecha de vencimiento**: Ajustar el plazo de pago
- **Marcación**: Referencia interna para la factura
- **Información de envío**: AWB, HAWB, DAE, agencia de carga
- **Fecha de entrega**: Actualizar cuando se entreguen los productos
- **Peso**: Actualizar el peso total

### Campos editables en facturas de proveedor:

- **Número de factura**: Actualizar con el número real del proveedor
- **Fecha de vencimiento**: Ajustar el plazo de pago
- **Información de envío**: Detalles logísticos

### Pasos para editar una factura:

1. Acceda al detalle de la factura que desea editar
2. Haga clic en el botón "Editar"
3. Actualice los campos necesarios
4. Haga clic en "Guardar"

**Limitaciones:** No se pueden editar los productos o valores de la factura. Si necesita modificar estos datos, debe anular la factura y crear una nueva.

## 7. Anulación de Facturas

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Invoices > [Número de Factura] > Anular

![Anulación de Factura]

La anulación cancela una factura y la marca como no válida.

### Pasos para anular una factura:

1. Acceda al detalle de la factura que desea anular
2. Haga clic en el botón "Anular Factura"
3. Confirme la acción cuando se le solicite
4. El sistema automáticamente:
   - Cambia el estado de la factura a "ANULADO"
   - Revierte la orden relacionada a estado "CONFIRMADO"
   - Elimina la referencia de factura en la orden

**Implicaciones:** Una vez anulada, una factura no puede ser restaurada. Deberá crear una nueva factura si es necesario.

## 8. Gestión de Pagos

**Ruta de acceso:** Menú Principal > Trade > Payments / Collections

![Gestión de Pagos]

El sistema permite registrar y hacer seguimiento de los pagos de facturas:

### Registro de pago de cliente (cobro):

1. Acceda a "Trade > Collections"
2. Haga clic en "Nuevo Cobro"
3. Seleccione el cliente
4. Ingrese la información del pago:
   - Fecha
   - Monto
   - Método de pago
   - Referencia
5. Seleccione las facturas a las que aplicará el pago
6. Distribuya el monto entre las facturas seleccionadas
7. Haga clic en "Registrar Cobro"

### Registro de pago a proveedor:

1. Acceda a "Trade > Payments"
2. Haga clic en "Nuevo Pago"
3. Seleccione el proveedor
4. Ingrese la información del pago:
   - Fecha
   - Monto
   - Método de pago
   - Referencia
5. Seleccione las facturas a las que aplicará el pago
6. Distribuya el monto entre las facturas seleccionadas
7. Haga clic en "Registrar Pago"

### Estado de las facturas:

- Una factura cambia automáticamente a estado "PAGADO" cuando el total pagado iguala o supera el valor de la factura.
- El sistema calcula el saldo pendiente restando los pagos recibidos del total de la factura.
- Puede visualizar el historial de pagos de cada factura en su vista de detalle.

## 9. Informes y Exportación

**Ruta de acceso:** Menú Principal > Trade > Customer/Supplier Invoices (botones de exportación)

![Informes y Exportación]

El sistema permite generar informes y exportar datos de facturas:

### Exportación a Excel:

1. En la lista de facturas, haga clic en el botón "Exportar a Excel"
2. El sistema generará un archivo Excel con todas las facturas visibles en la lista actual
3. El archivo incluirá todos los campos relevantes:
   - Número de factura
   - Cliente/Proveedor
   - Fechas
   - Estados
   - Totales
   - Productos

### Exportación a PDF:

1. En la lista de facturas, haga clic en el botón "Exportar a PDF"
2. El sistema generará un informe PDF con todas las facturas visibles
3. El informe incluirá un resumen y detalles de cada factura

### Impresión de factura individual:

1. Acceda al detalle de la factura
2. Haga clic en el botón "Imprimir"
3. El sistema generará un PDF con el formato oficial de factura
4. Este documento puede ser impreso o enviado por correo electrónico al cliente/proveedor

### Informes financieros:

El sistema proporciona varios informes financieros basados en las facturas:
- **Facturas por vencer**: Lista de facturas próximas a vencerse
- **Facturas vencidas**: Lista de facturas con pago retrasado
- **Resumen de ventas**: Totales facturados por período
- **Resumen de compras**: Totales de facturas de proveedores por período

## 10. Atajos y Consejos Avanzados

- **Facturación automática**: Las facturas de proveedores se generan automáticamente al crear una factura de cliente relacionada.
- **Actualización masiva**: Utilice los filtros para seleccionar múltiples facturas y aplicar acciones en lote.
- **Referencia cruzada**: Desde una factura, puede acceder directamente a la orden relacionada y viceversa.
- **Seguimiento de vencimientos**: Utilice el indicador de "días para vencimiento" para priorizar cobros y pagos.
- **Filtrado avanzado**: Combine criterios de búsqueda para localizar facturas específicas.
- **Reconciliación de pagos**: Revise regularmente las facturas pagadas parcialmente para completar su proceso.

### Mensajes del sistema

Durante la operación del módulo de Facturas, el sistema puede mostrar diversos mensajes informativos o de error:

| Mensaje | Significado | Acción recomendada |
|---------|-------------|-------------------|
| "Factura generada correctamente" | La factura se ha creado con éxito | Proceda a revisar los detalles |
| "La factura ha sido actualizada con éxito" | Los cambios se han guardado | Ninguna acción requerida |
| "Factura eliminada exitosamente" | La factura ha sido anulada | Ninguna acción requerida |
| "La orden no puede ser facturada" | Estado actual no permite facturación | Verifique que la orden esté confirmada |
| "Pago registrado exitosamente" | El pago se ha aplicado a la factura | Verifique el nuevo saldo pendiente |
| "Error al generar factura" | Problemas en la creación | Revise los datos de la orden |

### Campos especiales en facturas de exportación

Para las facturas de exportación (ventas internacionales), es importante completar correctamente los siguientes campos:

- **AWB/MAWB**: Número de guía aérea principal
- **HAWB**: Número de guía aérea hija o secundaria
- **DAE Exportación**: Número de documento aduanero de exportación
- **Agencia de Carga**: Empresa que maneja el transporte
- **Peso**: Peso total del envío en kilogramos

Estos datos son esenciales para el seguimiento logístico y la documentación aduanera.

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
