# Manual del Módulo de Pagos y Cobros

![Logo Kosmo Flowers]

## Introducción

El módulo de Pagos y Cobros de Kosmo Flowers permite gestionar eficientemente el flujo de efectivo de la empresa, facilitando el registro, seguimiento y control de todas las transacciones financieras relacionadas con las facturas de compra y venta. Este sistema integral ofrece herramientas para aplicar pagos a facturas de proveedores y registrar cobros de facturas de clientes, pudiendo manejar tanto pagos completos como parciales.

Este manual detalla las funcionalidades del módulo y proporciona instrucciones paso a paso para su uso eficiente.

## Índice

1. [Conceptos Básicos](#1-conceptos-básicos)
2. [Gestión de Cobros](#2-gestión-de-cobros)
3. [Gestión de Pagos](#3-gestión-de-pagos)
4. [Aplicación de Pagos/Cobros a Facturas](#4-aplicación-de-pagoscobros-a-facturas)
5. [Estado de Cuentas](#5-estado-de-cuentas)
6. [Métodos de Pago](#6-métodos-de-pago)
7. [Reportes Financieros](#7-reportes-financieros)
8. [Seguimiento de Vencimientos](#8-seguimiento-de-vencimientos)
9. [Anulación de Pagos/Cobros](#9-anulación-de-pagoscobros)
10. [Atajos y Consejos Avanzados](#10-atajos-y-consejos-avanzados)

---

## 1. Conceptos Básicos

El sistema de Pagos y Cobros de Kosmo Flowers maneja dos tipos principales de transacciones:

- **Cobros (Ingresos)**: Registros de pagos recibidos de clientes por facturas de venta.
- **Pagos (Egresos)**: Registros de pagos realizados a proveedores por facturas de compra.

Cada transacción tiene un ciclo de vida definido a través de diferentes estados:

| Estado | Descripción | Acciones permitidas |
|--------|-------------|---------------------|
| PENDIENTE | Pago/Cobro registrado pero no procesado | Editar, Confirmar, Anular |
| CONFIRMADO | Pago/Cobro verificado y aplicado | Solo visualización |
| RECHAZADO | Pago/Cobro que no pudo ser procesado | Solo visualización |
| ANULADO | Pago/Cobro cancelado | Solo visualización |

### Características principales:

- **Aplicación múltiple**: Un pago o cobro puede aplicarse a múltiples facturas.
- **Pagos parciales**: Permite registrar pagos parciales en facturas.
- **Seguimiento automático**: El sistema actualiza automáticamente el estado de las facturas cuando son pagadas total o parcialmente.
- **Documentación adjunta**: Permite adjuntar comprobantes de pago (transferencias, cheques, etc.).
- **Control financiero**: Proporciona reportes detallados del estado de pagos y cobros.

## 2. Gestión de Cobros

**Ruta de acceso:** Menú Principal > Trade > Collections

![Lista de Cobros]

Esta funcionalidad le permite:
- **Visualizar** todos los cobros registrados de clientes
- **Crear** nuevos registros de cobros
- **Aplicar** cobros a facturas pendientes
- **Hacer seguimiento** del estado de los cobros

### Información principal:

En la lista de cobros se muestra:
- **Número de cobro**: Identificador único
- **Cliente**: Entidad que realizó el pago
- **Fecha**: Cuándo se recibió el pago
- **Monto**: Valor total recibido
- **Método de pago**: Forma en que se recibió el pago
- **Estado**: Situación actual del cobro
- **Facturas aplicadas**: Facturas a las que se aplicó el cobro
- **Acciones**: Botones para gestionar el cobro

### Crear un nuevo cobro:

1. Acceda a "Trade > Collections"
2. Haga clic en "Nuevo Cobro"
3. Complete el formulario con la información requerida:
   - **Cliente**: Seleccione el cliente que realiza el pago
   - **Fecha**: Indique cuándo se recibió el pago
   - **Monto**: Ingrese el valor total recibido
   - **Método de pago**: Seleccione entre las opciones disponibles (transferencia, cheque, efectivo, etc.)
   - **Banco** (opcional): Institución financiera relacionada
   - **Nro. de cuenta** (opcional): Cuenta desde la que se realizó el pago
   - **Nro. de operación** (opcional): Referencia de la transacción
   - **Documento** (opcional): Adjunte comprobante de pago
4. Seleccione las facturas pendientes a las que desea aplicar el cobro
5. Distribuya el monto entre las facturas seleccionadas
6. Haga clic en "Registrar Cobro"

El sistema automáticamente:
- Registra el cobro con estado "PENDIENTE"
- Aplica los montos a las facturas seleccionadas
- Actualiza el saldo pendiente de cada factura
- Cambia el estado de las facturas completamente pagadas a "PAGADO"

## 3. Gestión de Pagos

**Ruta de acceso:** Menú Principal > Trade > Payments

![Lista de Pagos]

Esta funcionalidad le permite:
- **Visualizar** todos los pagos realizados a proveedores
- **Crear** nuevos registros de pagos
- **Aplicar** pagos a facturas pendientes
- **Hacer seguimiento** del estado de los pagos

### Información principal:

En la lista de pagos se muestra:
- **Número de pago**: Identificador único
- **Proveedor**: Entidad a la que se realizó el pago
- **Fecha**: Cuándo se efectuó el pago
- **Monto**: Valor total pagado
- **Método de pago**: Forma en que se realizó el pago
- **Estado**: Situación actual del pago
- **Facturas aplicadas**: Facturas a las que se aplicó el pago
- **Acciones**: Botones para gestionar el pago

### Crear un nuevo pago:

1. Acceda a "Trade > Payments"
2. Haga clic en "Nuevo Pago"
3. Complete el formulario con la información requerida:
   - **Proveedor**: Seleccione el proveedor al que realiza el pago
   - **Fecha**: Indique cuándo se efectuó el pago
   - **Monto**: Ingrese el valor total pagado
   - **Método de pago**: Seleccione entre las opciones disponibles (transferencia, cheque, efectivo, etc.)
   - **Banco** (opcional): Institución financiera relacionada
   - **Nro. de cuenta** (opcional): Cuenta desde la que se realizó el pago
   - **Nro. de operación** (opcional): Referencia de la transacción
   - **Documento** (opcional): Adjunte comprobante de pago
4. Seleccione las facturas pendientes a las que desea aplicar el pago
5. Distribuya el monto entre las facturas seleccionadas
6. Haga clic en "Registrar Pago"

El sistema automáticamente:
- Registra el pago con estado "PENDIENTE"
- Aplica los montos a las facturas seleccionadas
- Actualiza el saldo pendiente de cada factura
- Cambia el estado de las facturas completamente pagadas a "PAGADO"

## 4. Aplicación de Pagos/Cobros a Facturas

Una de las características más potentes del sistema es la capacidad de aplicar un solo pago o cobro a múltiples facturas, o distribuir pagos parciales en una o varias facturas.

### Aplicación a múltiples facturas:

1. Durante la creación de un pago o cobro, el sistema muestra todas las facturas pendientes del proveedor o cliente seleccionado
2. Marque las casillas de verificación de las facturas a las que desea aplicar el pago
3. El sistema mostrará:
   - Número de factura
   - Fecha de emisión
   - Monto total
   - Saldo pendiente
   - Campo para ingresar el monto a aplicar
4. Ingrese el monto que desea aplicar a cada factura
   - Para pago total: Ingrese el monto exacto del saldo pendiente
   - Para pago parcial: Ingrese un monto menor al saldo pendiente
5. El sistema verificará que la suma de los montos aplicados no supere el monto total del pago/cobro

### Distribución automática:

El sistema ofrece opciones para distribuir automáticamente el monto:
- **Por antigüedad**: Aplica primero a las facturas más antiguas
- **Por vencimiento**: Prioriza las facturas próximas a vencer
- **Proporcional**: Distribuye el monto proporcionalmente entre todas las facturas seleccionadas

### Seguimiento de pagos parciales:

Cuando se aplica un pago parcial a una factura:
1. La factura permanece en estado "PENDIENTE"
2. El sistema actualiza el saldo pendiente
3. La factura aparecerá en futuras selecciones con el saldo reducido
4. Cuando el saldo llega a cero mediante pagos sucesivos, la factura cambia automáticamente a estado "PAGADO"

## 5. Estado de Cuentas

**Ruta de acceso:** Menú Principal > Trade > Collections/Payments > Estado de Cuenta

![Estado de Cuenta]

El sistema proporciona vistas detalladas del estado de cuenta de cada cliente o proveedor:

### Estado de cuenta de clientes:

Muestra información detallada sobre:
- **Facturas emitidas**: Todas las facturas generadas al cliente
- **Pagos recibidos**: Todos los cobros registrados del cliente
- **Saldo pendiente**: Monto total por cobrar
- **Facturas vencidas**: Facturas que han superado su fecha de vencimiento
- **Antigüedad de saldos**: Clasificación de deudas por períodos (1-30 días, 31-60 días, etc.)
- **Historial de pagos**: Registro cronológico de todos los cobros recibidos

### Estado de cuenta de proveedores:

Muestra información detallada sobre:
- **Facturas recibidas**: Todas las facturas registradas del proveedor
- **Pagos realizados**: Todos los pagos efectuados al proveedor
- **Saldo pendiente**: Monto total por pagar
- **Facturas por vencer**: Facturas próximas a su fecha de vencimiento
- **Antigüedad de saldos**: Clasificación de deudas por períodos
- **Historial de pagos**: Registro cronológico de todos los pagos realizados

### Funciones adicionales:

- **Filtros por fecha**: Permite ver el estado de cuenta en un período específico
- **Exportación**: Opciones para exportar a Excel o PDF
- **Envío por correo**: Función para enviar el estado de cuenta directamente al cliente o proveedor

## 6. Métodos de Pago

El sistema admite diversos métodos de pago, cada uno con sus propias características:

| Método | Descripción | Campos adicionales |
|--------|-------------|-------------------|
| TRANSFERENCIA | Transferencia bancaria | Banco, Nro. cuenta, Nro. operación |
| CHEQUE | Pago mediante cheque | Banco, Nro. cheque, Fecha de cobro |
| EFECTIVO | Pago en efectivo | - |
| TARJETA DE CRÉDITO | Pago con TC | Banco, Nro. autorización |
| TARJETA DE DÉBITO | Pago con TD | Banco, Nro. autorización |
| NOTA DE CRÉDITO | Compensación | Nro. de nota de crédito |
| OTRO | Otros métodos | Descripción |

### Registrar pagos con diferentes métodos:

1. Al crear un pago o cobro, seleccione el método correspondiente
2. Complete los campos adicionales específicos del método seleccionado
3. Para pagos con cheque, puede registrar la fecha de cobro para seguimiento futuro
4. Para notas de crédito, debe indicar el número de documento de referencia

### Documentación adjunta:

Para todos los métodos de pago, es recomendable adjuntar un documento que respalde la transacción:
1. Use el campo "Documento" para subir un archivo
2. Formatos aceptados: JPG, PNG, PDF
3. Tamaño máximo: 5MB
4. Este documento estará disponible para consulta en el detalle del pago/cobro

## 7. Reportes Financieros

**Ruta de acceso:** Menú Principal > Trade > Collections/Payments > Reportes

![Reportes Financieros]

El sistema ofrece diversos reportes para análisis financiero:

### Reporte de cobros:

- **Cobros por período**: Detalle de todos los cobros en un rango de fechas
- **Cobros por cliente**: Agrupación de cobros recibidos por cliente
- **Cobros por método de pago**: Análisis de los métodos de pago utilizados
- **Cobros vs. Facturación**: Comparativa entre lo facturado y lo cobrado

### Reporte de pagos:

- **Pagos por período**: Detalle de todos los pagos en un rango de fechas
- **Pagos por proveedor**: Agrupación de pagos realizados por proveedor
- **Pagos por método de pago**: Análisis de los métodos utilizados
- **Flujo de caja de pagos**: Proyección de pagos futuros según vencimientos

### Reportes combinados:

- **Flujo de caja**: Balance entre cobros y pagos
- **Proyección financiera**: Estimación de ingresos y egresos futuros
- **Análisis de morosidad**: Detalle de facturas vencidas por cliente

### Exportación y personalización:

- Todos los reportes pueden exportarse a Excel o PDF
- Opciones para personalizar columnas visibles
- Filtros avanzados por cliente, proveedor, estado, etc.
- Gráficos y visualizaciones para análisis rápido

## 8. Seguimiento de Vencimientos

**Ruta de acceso:** Menú Principal > Trade > Collections/Payments > Vencimientos

![Seguimiento de Vencimientos]

Esta funcionalidad permite monitorear las facturas pendientes según su fecha de vencimiento:

### Facturas por cobrar:

- **Vencidas**: Facturas que han superado su fecha de vencimiento
- **Por vencer hoy**: Facturas que vencen en el día actual
- **Por vencer esta semana**: Vencimientos en los próximos 7 días
- **Por vencer este mes**: Vencimientos en los próximos 30 días
- **Futuras**: Vencimientos más allá de 30 días

### Facturas por pagar:

- **Vencidas**: Facturas que han superado su fecha de vencimiento
- **Por vencer hoy**: Facturas que vencen en el día actual
- **Por vencer esta semana**: Vencimientos en los próximos 7 días
- **Por vencer este mes**: Vencimientos en los próximos 30 días
- **Futuras**: Vencimientos más allá de 30 días

### Alertas y notificaciones:

El sistema puede configurarse para enviar alertas automáticas:
- Notificaciones de facturas próximas a vencer
- Alertas de facturas vencidas
- Recordatorios de seguimiento para cobros pendientes

### Acciones en lote:

Desde la vista de vencimientos, puede realizar acciones en lote:
- Registrar múltiples cobros para un mismo cliente
- Generar recordatorios automáticos
- Exportar listados para seguimiento manual

## 9. Anulación de Pagos/Cobros

**Ruta de acceso:** Menú Principal > Trade > Collections/Payments > [Seleccionar pago/cobro] > Anular

![Anulación de Pago/Cobro]

En ocasiones es necesario anular un pago o cobro registrado:

### Proceso de anulación:

1. Localice el pago o cobro que desea anular
2. Verifique que esté en estado "PENDIENTE" (no se pueden anular pagos "CONFIRMADOS")
3. Haga clic en el botón "Anular"
4. Confirme la acción cuando se le solicite
5. Opcionalmente, ingrese un motivo para la anulación

### Efectos de la anulación:

Cuando se anula un pago o cobro, el sistema:
1. Cambia el estado del pago/cobro a "ANULADO"
2. Revierte todas las aplicaciones a facturas
3. Restaura los saldos pendientes de las facturas afectadas
4. Revierte el estado de las facturas a "PENDIENTE" si estaban marcadas como "PAGADO"
5. Registra el usuario que realizó la anulación y la fecha

### Limitaciones:

- Solo los pagos/cobros en estado "PENDIENTE" pueden ser anulados
- Los usuarios necesitan permisos específicos para realizar anulaciones
- No se pueden editar pagos anulados, se debe crear uno nuevo si es necesario

## 10. Atajos y Consejos Avanzados

### Registro eficiente de pagos/cobros:

- **Agrupación inteligente**: Agrupe facturas del mismo cliente o proveedor para procesarlas en un solo pago
- **Plantillas de pago**: Utilice la función de plantillas para pagos recurrentes
- **Importación masiva**: Para volúmenes grandes, utilice la función de importación desde Excel

### Aplicación estratégica:

- **Priorización por vencimiento**: Aplique pagos primero a las facturas más próximas a vencer
- **Distribución óptima**: En caso de fondos limitados, distribuya pagos para mantener relaciones comerciales clave
- **Notas de crédito**: Utilice notas de crédito para compensar facturas específicas

### Seguimiento y control:

- **Revisión regular**: Establezca un día fijo para revisar el estado de cobros y pagos
- **Conciliación bancaria**: Compare los pagos/cobros registrados con los movimientos bancarios
- **Proyección de flujo**: Utilice los reportes de vencimiento para planificar su flujo de caja

### Integración con otros módulos:

- **Órdenes y Facturas**: Revise el estado de pago desde los módulos de órdenes y facturas
- **Informes gerenciales**: Utilice los datos de pagos para análisis financieros
- **Límites de crédito**: Monitoree los saldos pendientes para control de límites de crédito

### Mensajes del sistema

Durante la operación del módulo de Pagos y Cobros, el sistema puede mostrar diversos mensajes informativos o de error:

| Mensaje | Significado | Acción recomendada |
|---------|-------------|-------------------|
| "Pago registrado exitosamente" | El pago se ha creado correctamente | Proceda a confirmar el pago |
| "Cobro aplicado a facturas" | Las facturas seleccionadas han sido actualizadas | Verifique los nuevos saldos |
| "Pago anulado correctamente" | El pago ha sido marcado como anulado | Ninguna acción requerida |
| "Error: El total aplicado excede el monto del pago" | La suma de los montos aplicados es mayor que el total del pago | Ajuste los montos aplicados |
| "Error: No se seleccionaron facturas" | No se especificaron facturas para aplicar el pago | Seleccione al menos una factura |
| "Factura completamente pagada" | Una factura ha recibido el pago total | Ninguna acción requerida |

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
