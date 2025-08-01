# Manual de Usuario: Gestión de Socios de Negocio

Este manual le guiará a través de todas las funciones disponibles en el módulo de Socios de Negocio del sistema Kosmo Flowers, diseñado para administrar eficientemente sus relaciones comerciales con clientes y proveedores.

## ¿Qué puede hacer con el módulo de Socios de Negocio?

Este módulo le permite:
- Registrar nuevos clientes y proveedores con información detallada
- Gestionar datos fiscales y de contacto
- Configurar términos de crédito y márgenes de ganancia personalizados
- Visualizar estadísticas de ventas por cliente
- Administrar cuentas bancarias de sus socios
- Gestionar contactos para cada socio comercial
- Administrar documentos DAE (Declaración Aduanera de Exportación)
- Vincular proveedores con clientes específicos

## Guía de Pantallas y Funciones

### 1. Lista de Clientes
**Ruta de acceso:** Menú Principal > Socios > Clientes

![Lista de Clientes]

En esta pantalla usted puede:
- **Ver todos sus clientes** ordenados alfabéticamente
- **Buscar clientes** utilizando el campo de búsqueda en la parte superior
- **Visualizar estadísticas clave** para cada cliente:
  - Monto total facturado
  - Número de tallos vendidos
  - Pedidos pendientes por facturar
- **Exportar datos** a Excel o PDF usando los botones de la parte superior
- **Acceder al detalle** de cada cliente haciendo clic en su nombre
- **Crear nuevos clientes** mediante el botón "Nuevo Cliente"

**Consejo práctico:** Utilice los encabezados de columna para ordenar la lista según diferentes criterios (por ejemplo, por volumen de ventas o clientes con pedidos pendientes).

### 2. Lista de Proveedores
**Ruta de acceso:** Menú Principal > Socios > Proveedores

![Lista de Proveedores]

Esta pantalla funciona de manera similar a la lista de clientes, pero enfocada en sus proveedores. Aquí puede:
- **Administrar todos sus proveedores** en una vista unificada
- **Buscar proveedores específicos** por nombre, país o ciudad
- **Ver estadísticas relevantes** como montos de compra y facturas pendientes
- **Exportar la información** para análisis adicional
- **Crear nuevos proveedores** según sea necesario

**Consejo práctico:** Mantenga actualizada la información de sus proveedores para facilitar los procesos de compra y seguimiento de pedidos.

### 3. Crear Nuevo Socio de Negocio
**Ruta de acceso:** Menú Principal > Socios > Nuevo

![Formulario de Socio]

Para registrar un nuevo cliente o proveedor:
1. Complete el formulario con la siguiente información:
   - **RUC/Identificación fiscal:** Número de identificación tributaria
   - **Nombre:** Nombre completo de la empresa o persona
   - **Nombre corto:** Abreviatura o alias para identificación rápida
   - **Tipo de socio:** Seleccione CLIENTE o PROVEEDOR
   - **Dirección:** Dirección completa de la oficina principal
   - **País:** País donde se encuentra el socio
   - **Ciudad:** Ciudad de operación
   - **Datos de contacto:** Teléfono, correo electrónico, sitio web
   - **Términos de crédito:** Días de plazo para pago (0 para prepago)
   - **Rendimiento por defecto:** Margen de ganancia estándar
   - **Dirección de envío:** Para despacho de productos (si es diferente)
   - **Información adicional:** Referencia de carga, días de envío, etc.

2. Haga clic en "Guardar" para registrar el nuevo socio
3. Será redirigido a la vista de detalle donde podrá completar información adicional

**Nota importante:** Los campos marcados con * son obligatorios. Complete la mayor cantidad de información posible para facilitar las operaciones futuras.

### 4. Detalle de Socio de Negocio
**Ruta de acceso:** Menú Principal > Socios > Clientes/Proveedores > [Nombre del Socio]

![Detalle de Socio]

En esta pantalla puede:
- **Visualizar toda la información** del socio seleccionado
- **Editar los datos principales** mediante el botón "Editar"
- **Eliminar el socio** (con restricciones, ver sección "Importante")
- **Administrar cuentas bancarias** asociadas al socio
- **Gestionar contactos** (personas específicas dentro de la empresa)
- **Administrar documentos DAE** para clientes internacionales
- **Ver historial de operaciones** (facturas y pedidos)
- **Vincular proveedores** (si es un cliente) para definir qué productos puede comprar

**Funciones adicionales:**
- Para clientes, puede asignar proveedores específicos cuyos productos podrán comprar
- Para proveedores, puede consultar qué clientes tienen acceso a sus productos

### 5. Actualizar Socio de Negocio
**Ruta de acceso:** Menú Principal > Socios > Clientes/Proveedores > [Nombre del Socio] > Editar

Para actualizar la información de un socio existente:
1. Acceda a la pantalla de detalle del socio
2. Haga clic en el botón "Editar"
3. Modifique los campos necesarios en el formulario
4. Haga clic en "Guardar" para confirmar los cambios
5. Será redirigido a la vista de detalle con los cambios aplicados

**Nota importante:** La actualización de ciertos campos como tipo de socio o identificación fiscal puede afectar a operaciones existentes.

### 6. Eliminar Socio de Negocio
**Ruta de acceso:** Menú Principal > Socios > Clientes/Proveedores > [Nombre del Socio] > Eliminar

Para intentar eliminar un socio:
1. Acceda a la pantalla de detalle del socio
2. Haga clic en el botón "Eliminar"
3. Confirme la acción en el mensaje de advertencia

**¡IMPORTANTE!** Un socio de negocio **NO puede ser eliminado** si:
- Tiene pedidos asociados (órdenes de compra o venta)
- Tiene facturas emitidas o recibidas
- Está vinculado a otros registros activos del sistema

Si intenta eliminar un socio con dependencias, verá un mensaje: "No es posible eliminar el socio. Existen dependencias."

### 7. Gestión de Cuentas Bancarias
**Ruta de acceso:** Menú Principal > Socios > [Nombre del Socio] > Sección Bancos

En esta sección puede:
- **Ver todas las cuentas bancarias** registradas para el socio
- **Agregar nuevas cuentas** con información detallada
- **Editar cuentas existentes** 
- **Eliminar cuentas** que ya no se utilicen

Para agregar una nueva cuenta bancaria:
1. En la vista de detalle del socio, haga clic en "Agregar Banco"
2. Complete la información bancaria requerida
3. Haga clic en "Guardar"

**Consejo práctico:** Mantenga actualizada la información bancaria para facilitar los pagos y cobros.

### 8. Gestión de Contactos
**Ruta de acceso:** Menú Principal > Socios > [Nombre del Socio] > Sección Contactos

Esta funcionalidad le permite:
- **Registrar personas de contacto** dentro de la empresa del socio
- **Mantener información detallada** como cargo, teléfono, correo electrónico
- **Definir roles específicos** para cada contacto
- **Facilitar la comunicación directa** con las personas adecuadas

Para agregar un nuevo contacto:
1. En la vista de detalle del socio, haga clic en "Agregar Contacto"
2. Complete los datos personales y profesionales del contacto
3. Haga clic en "Guardar"

**Consejo práctico:** Asegúrese de registrar múltiples contactos con diferentes roles para garantizar siempre tener a quien dirigirse.

### 9. Gestión de DAE (Declaración Aduanera de Exportación)
**Ruta de acceso:** Menú Principal > Socios > [Nombre del Socio] > Sección DAE

Para clientes internacionales, puede:
- **Registrar documentos DAE** necesarios para exportación
- **Asociar DAE específicos** a facturas y envíos
- **Mantener un historial** de documentos aduaneros
- **Facilitar procesos de exportación** con toda la documentación a mano

## Operaciones Frecuentes y Consejos Prácticos

### Búsqueda Eficiente de Socios
Para encontrar rápidamente un socio específico:
1. Vaya a la lista de clientes o proveedores según corresponda
2. Utilice el campo de búsqueda en la parte superior
3. Puede buscar por nombre, identificación fiscal, país o ciudad
4. Los resultados se actualizan automáticamente mientras escribe

### Vinculación de Proveedores con Clientes
Para definir qué productos puede ver un cliente:
1. Acceda al detalle del cliente
2. Vaya a la sección "Proveedores Vinculados"
3. Seleccione los proveedores cuyos productos estará autorizado a comprar
4. Guarde los cambios

Esta funcionalidad es crucial para controlar qué productos puede ver y comprar cada cliente, especialmente útil cuando trabaja con diferentes proveedores y necesita gestionar el acceso a su catálogo.

### Gestión de Créditos y Márgenes
Para configurar términos financieros personalizados:
1. Edite el socio de negocio
2. Configure el "Plazo de crédito" en días (0 para prepago)
3. Establezca el "Rendimiento por defecto" según el margen deseado
4. Marque "Margen Incluido" si corresponde a su modelo de negocio

Estos parámetros influyen directamente en facturas, pagos y cálculos de rentabilidad.

### Auto-registro de Socios
El sistema permite que nuevos socios se registren de forma autónoma:
1. Acceda a "Socios > Auto-registro > Lista" para ver solicitudes pendientes
2. Revise la información proporcionada por cada potencial socio
3. Apruebe o rechace las solicitudes según sus criterios comerciales
4. Los socios aprobados pasarán automáticamente a su lista de clientes o proveedores

## Preguntas Frecuentes

### ¿Qué diferencia hay entre cliente y proveedor?
- **Cliente:** Compra sus productos. Se configuran en el sistema para facilitar ventas, facturación y cobros.
- **Proveedor:** Le vende productos. Se configuran para gestionar compras, recepción de mercancía y pagos.

Un mismo socio puede ser configurado como cliente y proveedor si mantiene ambas relaciones comerciales con su empresa.

### ¿Para qué sirve el "Rendimiento por defecto"?
El rendimiento por defecto representa el margen de ganancia estándar que se aplicará a los productos vendidos a ese cliente específico. Este valor se utiliza automáticamente al generar pedidos y facturas, aunque puede ser ajustado en cada operación.

### ¿Qué significa "Consolidado"?
La opción "Consolidado" indica que los envíos a este cliente pueden agruparse con otros en un mismo transporte para optimizar costos de envío. Esta configuración afecta a la logística y planificación de despachos.

### ¿Por qué no puedo eliminar algunos socios?
Un socio no puede ser eliminado si está siendo utilizado en otras partes del sistema, como:
- Pedidos (realizados o recibidos)
- Facturas (emitidas o recibidas)
- Stocks o inventarios vinculados

Esto garantiza la integridad de los datos históricos y evita inconsistencias en el sistema.

### ¿Cómo puedo saber si un cliente tiene buena salud financiera?
En la lista de clientes, puede ver estadísticas clave como:
- Monto total facturado
- Historial de pagos
- Pedidos pendientes

Adicionalmente, puede consultar los reportes financieros para un análisis más detallado de cada cliente.

## Aspectos Técnicos Importantes

### Formato de Datos
- **RUC/Identificación fiscal:** Formato según normativa del país
- **Nombres:** Se recomienda usar nombres completos y oficiales
- **Correos electrónicos:** Verificar que sean correctos para asegurar comunicación efectiva
- **Términos de crédito:** Valor numérico en días (0 significa pago anticipado)

### Combinación con Otros Módulos
El módulo de Socios de Negocio está conectado con:
- **Pedidos:** Para crear órdenes de compra o venta
- **Facturación:** Para emitir y recibir facturas
- **Pagos y Cobros:** Para gestionar transacciones financieras
- **Catálogo de Productos:** Para definir qué productos puede ver cada cliente

## Mensajes y Notificaciones

Durante la gestión de socios, el sistema mostrará diferentes mensajes:

| Mensaje | Significado | Acción Recomendada |
|---------|-------------|-------------------|
| "El socio ha sido creado con éxito" | El nuevo socio se ha registrado correctamente | Puede continuar agregando información adicional |
| "El socio ha sido actualizado con éxito" | Los cambios se han guardado correctamente | Verifique los datos en la vista de detalle |
| "¿Está seguro que desea eliminar el socio?" | Confirmación antes de eliminar | Considere las implicaciones antes de confirmar |
| "No es posible eliminar el socio. Existen dependencias." | El socio está siendo utilizado | Revise dónde se utiliza el socio antes de intentar eliminarlo |

---

## Atajos y Consejos Avanzados

- **Filtrado avanzado:** Combine búsqueda por texto con ordenamiento por columnas para encontrar rápidamente socios específicos
- **Exportación de datos:** Utilice las funciones de exportación para análisis externos o respaldos
- **Actualizaciones masivas:** Para actualizar información similar en múltiples socios, use la exportación/importación Excel
- **Verificación periódica:** Revise regularmente la información de contacto para mantenerla actualizada

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
