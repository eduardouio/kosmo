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
   - **RUC/Identificación fiscal:** Número de identificación tributaria - *Campo obligatorio*
   - **Nombre:** Nombre completo de la empresa o persona - *Campo obligatorio*
   - **Tipo de socio:** Seleccione CLIENTE o PROVEEDOR - *Campo obligatorio*
   - **Nombre corto:** Abreviatura o alias para identificación rápida
   - **Dirección:** Dirección completa de la oficina principal - *Campo obligatorio*
   - **País:** País donde se encuentra el socio - *Campo obligatorio*
   - **Ciudad:** Ciudad de operación - *Campo obligatorio*
   - **Datos de contacto:** Teléfono, correo electrónico, sitio web
   - **Términos de crédito:** Días de plazo para pago (0 para prepago)
   - **Rendimiento por defecto:** Margen de ganancia estándar
   - **Dirección de envío:** Para despacho de productos (si es diferente)
   - **Información adicional:** Referencia de carga, días de envío, etc.

2. Haga clic en "Guardar" para registrar el nuevo socio
3. Será redirigido a la vista de detalle donde podrá completar información adicional

**Detalle de los campos del modelo:**

| Campo | Descripción | Tipo | Obligatorio | Valor predeterminado |
|-------|-------------|------|-------------|----------------------|
| RUC | Número de identificación fiscal | Texto (máx. 15 caracteres) | Sí | Ninguno |
| Nombre | Nombre de la empresa o persona | Texto (máx. 255 caracteres) | Sí | Ninguno |
| Tipo de Socio | Clasificación como CLIENTE o PROVEEDOR | Selección | Sí | Ninguno |
| Estado | Estado de aprobación del socio | Selección | No | "APROBADO" |
| Fecha de Aprobación | Fecha en que se aprobó al socio | Fecha | No | Ninguno |
| Nombre Corto | Alias o abreviatura | Texto (máx. 50 caracteres) | No | Ninguno |
| Dirección | Ubicación principal | Texto (máx. 255 caracteres) | Sí | Ninguno |
| País | País de residencia | Texto (máx. 50 caracteres) | Sí | Ninguno |
| Ciudad | Ciudad principal | Texto (máx. 50 caracteres) | Sí | Ninguno |
| Código de Área | Prefijo telefónico | Texto (máx. 10 caracteres) | No | Ninguno |
| Código Postal | Código postal o ZIP | Texto (máx. 10 caracteres) | No | Ninguno |
| Sitio Web | Dirección web | Texto (máx. 255 caracteres) | No | Ninguno |
| Margen Incluido | Si el margen está incluido en precio | Booleano | No | False |
| Rendimiento por defecto | Margen de ganancia estándar | Número decimal | No | 0.00 |
| Plazo de crédito | Días de crédito otorgados | Número entero | No | 0 |
| Teléfono | Teléfono principal | Texto (máx. 20 caracteres) | No | Ninguno |
| Teams | Usuario de Microsoft Teams | Texto (máx. 50 caracteres) | No | Ninguno |
| Dirección de Envío | Dirección para despachos | Texto (máx. 255 caracteres) | No | Ninguno |
| Correo Electrónico | Email principal | Correo electrónico | No | Ninguno |
| Correo de Pago | Email para facturas/pagos | Correo electrónico | No | Ninguno |
| Días de Envío | Días para despacho | Número entero | No | Ninguno |
| Referencia de Carga | Transportista preferido | Texto (máx. 255 caracteres) | No | Ninguno |
| Años en el mercado | Experiencia en el sector | Número entero | No | 0 |
| Consolidado | Si acepta envíos consolidados | Booleano | No | False |
| Vendedor | Representante asignado | Texto (máx. 100 caracteres) | No | Ninguno |

**Nota importante:** Los campos marcados como obligatorios deben completarse para poder guardar el registro. El sistema convertirá automáticamente a mayúsculas la mayoría de los campos de texto.

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

![Gestión de Bancos]

En esta sección puede:
- **Ver todas las cuentas bancarias** registradas para el socio
- **Agregar nuevas cuentas** con información detallada
- **Editar cuentas existentes** 
- **Eliminar cuentas** que ya no se utilicen

Para agregar una nueva cuenta bancaria:
1. En la vista de detalle del socio, haga clic en "Agregar Banco"
2. Complete el formulario con la siguiente información:
   - **Propietario:** Nombre del titular de la cuenta - *Campo obligatorio*
   - **DNI/RUC/CI:** Identificación del titular - *Campo obligatorio*
   - **Nombre del Banco:** Entidad bancaria - *Campo obligatorio*
   - **Número de Cuenta:** Número de cuenta completo - *Campo obligatorio*
   - **Banco Nacional:** Marque si es un banco del país
   - **Código SWIFT:** Para transferencias internacionales
   - **IBAN:** Código internacional de cuenta bancaria

3. Haga clic en "Guardar"

**Detalle de los campos del modelo Banco:**

| Campo | Descripción | Tipo | Obligatorio | Valor predeterminado |
|-------|-------------|------|-------------|----------------------|
| Propietario | Nombre del titular de la cuenta | Texto (máx. 255 caracteres) | Sí | Ninguno |
| DNI/RUC/CI | Identificación fiscal del titular | Texto (máx. 15 caracteres) | Sí | Ninguno |
| Número de Cuenta | Número completo de la cuenta | Texto (máx. 50 caracteres) | Sí | Ninguno |
| Nombre del Banco | Entidad bancaria | Texto (máx. 100 caracteres) | Sí | Ninguno |
| Código SWIFT | Código para transferencias internacionales | Texto (máx. 50 caracteres) | No | Ninguno |
| IBAN | Código internacional de cuenta | Texto (máx. 50 caracteres) | No | Ninguno |
| Banco Nacional | Si es un banco del país local | Booleano | No | True |

**Consejo práctico:** Para transferencias internacionales, asegúrese de incluir los códigos SWIFT e IBAN correctos para evitar rechazos o demoras en los pagos.

### 8. Gestión de Contactos
**Ruta de acceso:** Menú Principal > Socios > [Nombre del Socio] > Sección Contactos

![Gestión de Contactos]

Esta funcionalidad le permite:
- **Registrar personas de contacto** dentro de la empresa del socio
- **Mantener información detallada** como cargo, teléfono, correo electrónico
- **Definir roles específicos** para cada contacto
- **Facilitar la comunicación directa** con las personas adecuadas

Para agregar un nuevo contacto:
1. En la vista de detalle del socio, haga clic en "Agregar Contacto"
2. Complete el formulario con los siguientes datos:
   - **Nombre:** Nombre completo del contacto - *Campo obligatorio*
   - **Tipo de Contacto:** Rol dentro de la empresa (COMERCIAL, FINANCIERO, LOGÍSTICA, GERENCIA, OTRO) - *Campo obligatorio*
   - **Cargo:** Posición que ocupa en la empresa
   - **Teléfono:** Número de contacto directo
   - **Correo Electrónico:** Dirección de email profesional
   - **Principal:** Marque si es el contacto primario

3. Haga clic en "Guardar"

**Detalle de los campos del modelo Contacto:**

| Campo | Descripción | Tipo | Obligatorio | Valor predeterminado |
|-------|-------------|------|-------------|----------------------|
| Nombre | Nombre completo del contacto | Texto (máx. 255 caracteres) | Sí | Ninguno |
| Tipo de Contacto | Categoría funcional | Selección | No | "COMERCIAL" |
| Cargo | Posición en la empresa | Texto (máx. 255 caracteres) | No | Ninguno |
| Teléfono | Número telefónico | Texto (máx. 20 caracteres) | No | Ninguno |
| Correo Electrónico | Email de contacto | Correo electrónico | No | Ninguno |
| Principal | Si es el contacto principal | Booleano | No | False |

**Consejo práctico:** Designe siempre un contacto como "Principal" para cada socio, esto facilitará saber a quién dirigirse primero cuando sea necesario.

### 9. Gestión de DAE (Declaración Aduanera de Exportación)
**Ruta de acceso:** Menú Principal > Socios > [Nombre del Socio] > Sección DAE

![Gestión de DAE]

Para clientes internacionales, puede:
- **Registrar documentos DAE** necesarios para exportación
- **Asociar DAE específicos** a facturas y envíos
- **Mantener un historial** de documentos aduaneros
- **Facilitar procesos de exportación** con toda la documentación a mano

Para agregar un nuevo DAE:
1. En la vista de detalle del socio, haga clic en "Agregar DAE"
2. Complete el formulario con la siguiente información:
   - **DAE:** Número de Declaración Aduanera de Exportación - *Campo obligatorio*
   - **Fecha de Inicio:** Fecha desde la que es válido el documento - *Campo obligatorio*
   - **Fecha de Fin:** Fecha de vencimiento del documento - *Campo obligatorio*
   - **MAWB:** Número de guía aérea principal (Master Air Waybill)
   - **HAWB:** Número de guía aérea secundaria (House Air Waybill)
   - **Agencia de Carga:** Empresa responsable del transporte

3. Haga clic en "Guardar"

**Detalle de los campos del modelo DAE:**

| Campo | Descripción | Tipo | Obligatorio | Valor predeterminado |
|-------|-------------|------|-------------|----------------------|
| DAE | Número de Declaración Aduanera | Texto (máx. 50 caracteres) | Sí | Ninguno |
| Fecha de Inicio | Fecha de emisión | Fecha | Sí | Ninguno |
| Fecha de Fin | Fecha de vencimiento | Fecha | Sí | Ninguno |
| MAWB | Guía aérea principal | Texto (máx. 50 caracteres) | No | Ninguno |
| HAWB | Guía aérea secundaria | Texto (máx. 50 caracteres) | No | Ninguno |
| Agencia de Carga | Empresa transportista | Texto (máx. 50 caracteres) | No | Ninguno |

**Importante:** El número DAE debe ser único en el sistema. Verifique siempre que la fecha de vencimiento sea correcta para evitar problemas en aduana.

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
