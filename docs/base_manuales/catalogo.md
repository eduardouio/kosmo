# Manual de Usuario: Catálogo de Productos

Este manual le guiará a través de todas las funciones disponibles en el módulo de Catálogo de Productos del sistema Kosmo Flowers, diseñado para facilitar la gestión de su inventario de flores y variedades.

## ¿Qué puede hacer con el Catálogo de Productos?

El Catálogo de Productos le permite:
- Registrar nuevos productos (flores) con sus variedades
- Consultar y buscar productos existentes
- Ver estadísticas de ventas por producto
- Actualizar información de productos
- Gestionar imágenes de productos
- Definir colores disponibles para cada variedad
- Establecer márgenes de rendimiento personalizados
- Exportar su catálogo en diferentes formatos

## Guía de Pantallas y Funciones

### 1. Lista de Productos
**Ruta de acceso:** Menú Principal > Catálogo > Lista

![Lista de Productos]

En esta pantalla usted puede:
- **Ver todos sus productos** ordenados alfabéticamente
- **Buscar productos** utilizando el campo de búsqueda en la parte superior
- **Visualizar estadísticas mensuales** para cada producto:
  - Número de tallos vendidos
  - Cantidad de facturas generadas
  - Total de ventas ($)
  - Precio máximo y mínimo registrado
- **Exportar datos** a Excel o PDF usando los botones de la parte superior
- **Seleccionar varios productos** para edición masiva
- **Acceder al detalle** de cada producto haciendo clic en su nombre

**Consejo práctico:** Utilice la función de exportación a Excel para realizar análisis más detallados de su inventario y ventas.

### 2. Crear Nuevo Producto
**Ruta de acceso:** Menú Principal > Catálogo > Nuevo Producto

![Formulario de Producto]

Para crear un nuevo producto:
1. Complete el formulario con los siguientes datos:
   - **Nombre:** Nombre de la flor (se convertirá a mayúsculas automáticamente)
   - **Variedad:** Variedad específica de la flor (se convertirá a mayúsculas)
   - **Imagen:** Foto del producto (opcional pero recomendado)
   - **Colores:** Lista de colores disponibles, separados por comas
   - **Rendimiento por defecto:** Valor monetario de rendimiento (predeterminado: 0.06 USD)
   - **Notas:** Información adicional relevante
2. Haga clic en "Guardar"
3. Será redirigido a la vista de detalle del producto creado

**Consejo práctico:** Proporcione nombres y variedades descriptivos para facilitar la búsqueda posterior. Las imágenes de alta calidad ayudan a identificar visualmente los productos.

### 3. Detalle de Producto
**Ruta de acceso:** Menú Principal > Catálogo > Lista > [Nombre del Producto]

![Detalle de Producto]

En esta pantalla puede:
- **Visualizar toda la información** del producto seleccionado
- **Ver la imagen** del producto en mayor tamaño
- **Revisar los colores disponibles** mostrados como etiquetas
- **Consultar el rendimiento** establecido para el producto
- **Leer notas adicionales** sobre el producto
- **Actualizar la información** mediante el botón "Editar"
- **Eliminar el producto** (con restricciones, ver sección "Importante")

**Consejo práctico:** Desde esta pantalla puede navegar directamente a la edición del producto o volver al listado completo.

### 4. Actualizar Producto
**Ruta de acceso:** Menú Principal > Catálogo > Lista > [Nombre del Producto] > Editar

Para actualizar un producto existente:
1. Acceda a la pantalla de detalle del producto
2. Haga clic en el botón "Editar"
3. Modifique los campos necesarios en el formulario
4. Haga clic en "Guardar" para confirmar los cambios
5. Será redirigido a la vista de detalle con los cambios aplicados

**Nota importante:** Todos los campos pueden ser modificados. Si actualiza la imagen, la anterior será reemplazada.

### 5. Eliminar Producto
**Ruta de acceso:** Menú Principal > Catálogo > Lista > [Nombre del Producto] > Eliminar

Para intentar eliminar un producto:
1. Acceda a la pantalla de detalle del producto
2. Haga clic en el botón "Eliminar"
3. Confirme la acción en el mensaje de advertencia

**¡IMPORTANTE!** Un producto **NO puede ser eliminado** si:
- Ha sido incluido en cualquier stock
- Aparece en algún pedido de cliente o proveedor
- Se encuentra en alguna factura

Si intenta eliminar un producto con dependencias, verá un mensaje: "No es posible eliminar el producto. Existen dependencias."

## Operaciones Frecuentes y Consejos Prácticos

### Búsqueda Eficiente de Productos
Para encontrar rápidamente un producto específico:
1. Vaya a la lista de productos
2. Utilice el campo de búsqueda en la parte superior
3. Puede buscar por nombre, variedad o color
4. Los resultados se actualizan automáticamente mientras escribe

### Edición Masiva de Productos
Si necesita actualizar varios productos a la vez:
1. En la lista de productos, marque las casillas de los productos que desea modificar
2. Haga clic en el botón "Edición Masiva" en la parte superior
3. Seleccione qué campos desea actualizar para todos los productos seleccionados
4. Ingrese los nuevos valores
5. Confirme los cambios

### Análisis de Rendimiento de Productos
Para analizar qué productos son más rentables:
1. Acceda a la lista de productos
2. Observe las estadísticas mensuales para cada producto
3. Exporte la lista a Excel para un análisis más detallado
4. Ordene por columnas para identificar productos con mayor volumen o rentabilidad

### Gestión de Imágenes de Productos
Para obtener mejores resultados con las imágenes:
1. Utilice fotografías nítidas y bien iluminadas
2. Mantenga un fondo consistente para todas las imágenes
3. Asegúrese de que la flor sea claramente visible
4. Las dimensiones recomendadas son 800x600 píxeles

## Preguntas Frecuentes

### ¿Cómo se organizan los productos en el sistema?
Los productos se organizan principalmente por nombre y variedad. Cada producto representa un tipo de flor (por ejemplo, "ROSA") y cada variedad representa una variación específica de esa flor (por ejemplo, "FREEDOM"). Esta estructura facilita la organización y búsqueda en el catálogo.

### ¿Para qué sirve el campo "Colores"?
El campo "Colores" permite registrar todos los colores disponibles para una variedad específica. Esto es útil para:
- Identificar rápidamente qué colores ofrece cada variedad
- Facilitar la búsqueda de productos por color
- Proporcionar información visual a través de etiquetas de colores en la vista de detalle

### ¿Qué significa el "Rendimiento por defecto"?
El rendimiento por defecto (predeterminado en 0.06 USD) representa el margen de ganancia estándar por tallo para ese producto específico. Este valor se utiliza automáticamente en cálculos de precios y estimaciones de ganancia en pedidos y facturas.

### ¿Por qué no puedo eliminar algunos productos?
Un producto no puede ser eliminado si está siendo utilizado en otras partes del sistema. Esto incluye:
- Productos incluidos en inventarios (stocks)
- Productos que aparecen en pedidos (órdenes de compra o venta)
- Productos facturados a clientes o proveedores

Esto garantiza la integridad de los datos históricos y evita inconsistencias en el sistema.

### ¿Cómo puedo saber si un producto se vende bien?
En la lista de productos, puede ver estadísticas mensuales para cada producto, incluyendo:
- Cantidad de tallos vendidos
- Número de facturas en las que aparece
- Total de ventas generadas
- Precios máximos y mínimos

Estas métricas le ayudarán a identificar sus productos más populares y rentables.

## Aspectos Técnicos Importantes

### Combinación con Otros Módulos
El catálogo de productos está conectado con otros módulos del sistema:
- **Inventario (Stocks):** Los productos del catálogo se utilizan para registrar existencias
- **Pedidos:** Los clientes pueden solicitar productos específicos del catálogo
- **Facturación:** Los productos vendidos se registran en facturas con sus precios correspondientes

## Mensajes y Notificaciones

Durante la gestión de productos, el sistema mostrará diferentes mensajes:

| Mensaje | Significado | Acción Recomendada |
|---------|-------------|-------------------|
| "El producto ha sido creado con éxito" | El nuevo producto se ha registrado correctamente | Puede continuar usando el producto en otras operaciones |
| "El producto ha sido actualizado con éxito" | Los cambios se han guardado correctamente | Verifique los datos en la vista de detalle |
| "¿Está seguro que desea eliminar el producto?" | Confirmación antes de eliminar | Considere las implicaciones antes de confirmar |
| "No es posible eliminar el producto. Existen dependencias." | El producto está siendo utilizado | Revise dónde se utiliza el producto antes de intentar eliminarlo |

---

## Atajos y Consejos Avanzados

- **Copiar producto existente:** Para crear un producto similar a uno existente, edite el producto original y use "Guardar como nuevo"
- **Filtrado avanzado:** Combine búsqueda por texto con ordenamiento por columnas para encontrar rápidamente productos específicos
- **Etiquetas visuales:** Los colores se muestran como etiquetas visuales para facilitar la identificación
- **Vista previa de imágenes:** Pase el cursor sobre las miniaturas para ver una versión ampliada

---

¿Necesita ayuda adicional? Contacte al equipo de soporte técnico o consulte los videos tutoriales disponibles en la sección de ayuda del sistema.

![Logo Kosmo Flowers]
