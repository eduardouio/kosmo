
## Reunión Kosmo

### 1. Carga manual desde archivo
- Generar una funcionalidad para la carga manual desde un archivo con formato específico, para cuando OpenAI no esté disponible.

---

### 2. Fichas de socio de negocios
- En el formulario de socio de negocios se deben agregar los campos:
  - Contacto
  - E-mail de pagos
  - Skype
  - Web
- Cambiar la etiqueta de **RUC** a **ID/RUC/TAX ID**.
- Clasificar a los socios en dos categorías, en páginas y menús diferentes:
  - Proveedores
  - Clientes
- Agregar campos para **2 referencias** en la ficha de socio de negocio.
- Crear un formulario para el alta de los socios de negocio para posterior aprobación conforme el formato.
- Incluir en el formulario de alta:
  - Términos y condiciones de Kosmo.
  - Política de crédito.
  - Política de perecibilidad de las flores.
  - Notas de crédito con plazo de **10 días**.

---

### 3. Vendedores
- Los vendedores no pueden ver el proveedor de las flores, solo se mostrará Kosmo como proveedor en el stock.
- Las órdenes de los vendedores deben ser aprobadas por el administrador.
- La pantalla de los vendedores mostrará información de su progreso mensual.

---

### Catálogo de flores
- Agregar **múltiples colores** por producto en la ficha del catálogo, permitiendo:
  - Filtrar por color las variedades.
  - Ofrecer un color similar en una variedad diferente.
- Permitir consultas por color en:
  - La tabla de stocks.
  - El catálogo de productos.

---

### Pedidos y facturación
#### 1. Características de los pedidos
- Incorporar el rendimiento en las tablas de pedido.
- Asegurar un margen positivo en cada pedido.
- Campos relevantes para los pedidos:
  - Variedad
  - Tamaño
  - Costo
  - Precio de venta (automático)
  - Rentabilidad (basada en el catálogo)
  - Tipo de caja

#### 2. Facturación
- Cargar facturas de proveedores al sistema.
- Asegurar que los valores de las facturas coincidan con los pedidos.
- Agregar el precio de compra en las órdenes de compra (no en el stock).

#### 3. Disposición
- Permitir la edición de la disposición del pedido.

---

### Control para vendedores
- Los vendedores:
  - No deben conocer las fincas de origen; solo se muestra Kosmo como proveedor.
  - No deben tener acceso a las fichas de los socios de negocio.
  - Se crean mediante un formulario específico.
  - Reciben una comisión basada en:
    - Porcentaje de ganancia.
    - Valor por tallo.
- Cuando se comparte la disposición, se incrementa en **2 ctv** automáticamente.
- Implementar una meta visual para los vendedores utilizando colores.

---

### Créditos y reclamos
- Los clientes tienen **10 días laborables** para realizar reclamos.
- Enviar un correo al finalizar este periodo informando que ya no es posible presentar reclamos.
- Reclamos posteriores a este plazo no serán considerados para créditos.







```text
Reunion Kosmo

Generar, la carga manual desde un archivo con formato

EL CONTACTO
E-MAIL DE PAGOS
SKYPE
WEB

DEBE TENER ESOS campo

El Ruc de forma interna el 


Publicar ficha de socio de negocios en linea, kosmo aprueba y se registra
Proveedor y otro para cliente
Hacer que el envío sea mediante un botón


REFERENCIA CARGUERA
CONTACTO
TELEFONO
REFERENCIAS FINCA 1
CONTACTO
TELEFONO
REFERENCIAS FINCA 2

En carguera por ejemplo 
Agregar las referencias (2)

El formulario debe alimentar la base con el formato, 

En el formulario de clientes poner el un botón de aceptar el registro, enviar con el acepto del las condiciones y políticas
Politics de credit y de perecibilidad de las flores


Notas, confuso al momento de 



En socio de negocio poner dos menos, el de clientes y de proveedores y ejecutivos de venta


￼


En catalogo de flores, poner coloren en la ficha del producto 
	VARIOS COLORES POR PRODUCTO,

Debo poder consultar por color en la tabla, tanto de stocks y el catalogo



Hacer los cambios en el pedido
Cargar las facturas de los proveedores en el sistema para empatar el valor
Ver si se puede poner el precio de compra.

Todo es en la orden de copra no en el stock del producto
Poner el rendimiento en las tablas de pedido
Siempre va a haber un margen positivo

Variedad
Tamano
Costo
precio de Venta (automatico)
Rentabilidad (usar la del catalogo)
Tipo de caja



Si se debe poder editar la disposición
Los vendedores no debe saber de que finca es solo se muestra del proveedor kosmo, las demás no se muestra el proveedor


Vendedor, no puede ver las fichas de los socios de negocios, el vendedor también se crea en una formulario
Se le paga un porcentaje o un valor por tallo, ver como se asigna el porcentaje de ganancia por % o por tallo
Cuando comparte la disto a los vendedores se le sube 2ctvs
Una meta usando elementos visuales por color


Creditos

El cliente tiene 10 días laborables para hacer un reclamo, se envia un correo a los 10 días no puede hacer reclamos, por ende créditos, 

```