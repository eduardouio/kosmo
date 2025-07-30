# Tests para Payment APIs

## Descripción

Esta suite de tests cubre los endpoints de pagos (`PaymentCreateUpdateAPI` y `PaymentDeleteAPI`) de manera exhaustiva, incluyendo casos de éxito, errores y escenarios de integración.

## Archivos de Test

### 1. `test_PaymentCreateUpdateAPI.py`
Contiene tests para el endpoint de creación y actualización de pagos:

**Casos de Creación:**
- ✅ Crear pago exitosamente con múltiples facturas
- ❌ Crear pago sin campos requeridos
- ❌ Crear pago sin facturas
- ❌ Crear pago donde el monto no coincide con la suma de facturas
- ❌ Crear pago con factura inexistente
- ❌ Crear pago con método que requiere banco pero no se proporciona
- ❌ Crear pago con JSON inválido
- ❌ Crear pago con body vacío

**Casos de Actualización:**
- ✅ Actualizar pago exitosamente
- ❌ Actualizar pago que no existe
- ❌ Actualizar pago ya confirmado/rechazado

**Casos de Consulta:**
- ✅ Obtener detalles de un pago específico
- ❌ Obtener pago que no existe
- ✅ Listar pagos con paginación

### 2. `test_PaymentDeleteAPI.py`
Contiene tests para el endpoint de eliminación de pagos:

**Eliminación Múltiple:**
- ✅ Eliminar múltiples pagos exitosamente
- ⚠️ Eliminar pagos con resultados mixtos (algunos se pueden, otros no)
- ❌ Eliminar sin proporcionar payment_ids
- ❌ Eliminar con lista vacía
- ❌ Eliminar con tipo de dato inválido
- ❌ Eliminar pagos que no existen
- ❌ Eliminar pagos que no se pueden eliminar (confirmados/rechazados)

**Eliminación Individual:**
- ✅ Eliminar un pago específico exitosamente
- ❌ Eliminar pago que no existe
- ❌ Eliminar pago confirmado o rechazado

**Casos de Error:**
- ❌ JSON inválido
- ❌ Body vacío

### 3. `test_PaymentAPIsIntegration.py`
Contiene tests de integración que prueban flujos completos:

**Flujos Completos:**
- ✅ Ciclo completo: crear → obtener → actualizar → eliminar
- ✅ Múltiples pagos aplicados a la misma factura
- ✅ Pago distribuido entre múltiples facturas
- ⚠️ Secuencia de manejo de errores
- ✅ Paginación y listado

## Cómo Ejecutar los Tests

### Ejecutar todos los tests de pagos:
```bash
cd /Users/eduardo/Repositorios/kosmo/app/src
python -m pytest tests/api/test_Payment*.py -v
```

### Ejecutar tests específicos:
```bash
# Solo tests de creación/actualización
python -m pytest tests/api/test_PaymentCreateUpdateAPI.py -v

# Solo tests de eliminación
python -m pytest tests/api/test_PaymentDeleteAPI.py -v

# Solo tests de integración
python -m pytest tests/api/test_PaymentAPIsIntegration.py -v
```

### Ejecutar un test específico:
```bash
python -m pytest tests/api/test_PaymentCreateUpdateAPI.py::TestPaymentCreateUpdateAPI::test_create_payment_success -v
```

### Ejecutar con cobertura:
```bash
python -m pytest tests/api/test_Payment*.py --cov=api.trade --cov-report=html
```

## Fixtures y Datos de Prueba

Cada clase de test incluye los siguientes fixtures:

### Datos Básicos:
- **Usuario**: Usuario autenticado para las pruebas
- **Cliente**: Partner de tipo CLIENTE
- **StockDay**: Día de stock activo
- **Orden**: Orden de venta confirmada

### Datos Específicos:
- **Facturas**: 1-2 facturas pendientes de pago
- **Pagos**: Pagos en diferentes estados (pendiente, confirmado, rechazado)
- **Detalles de Pago**: Relaciones entre pagos y facturas

## Validaciones Cubiertas

### Reglas de Negocio:
1. **Monto del pago** = Suma de montos de facturas
2. **Métodos de pago** con transferencia/tarjetas requieren banco y número de operación
3. **Estados de pago**: Solo se pueden modificar/eliminar pagos PENDIENTES
4. **Soft Delete**: Los pagos se desactivan, no se eliminan físicamente
5. **Cascada**: Al eliminar un pago, se desactivan sus PaymentDetail

### Validaciones de Entrada:
1. **Campos requeridos**: date, amount, method, invoices
2. **Tipos de datos**: Decimales para montos, listas para facturas
3. **Formato JSON**: Validación de JSON bien formado
4. **Existencia**: Validación de que las facturas existan

### Casos Limite:
1. **Pagos parciales**: Un pago puede cubrir parte de una factura
2. **Pagos múltiples**: Varias facturas en un solo pago
3. **Facturas compartidas**: Múltiples pagos a la misma factura
4. **Paginación**: Listado con grandes volúmenes de datos

## Cobertura Esperada

Los tests cubren:
- ✅ **Casos de éxito** (200, 201)
- ✅ **Errores de cliente** (400, 404)
- ✅ **Errores de validación** (ValidationError)
- ✅ **Casos mixtos** (207 - Partial Success)
- ✅ **Flujos de integración**
- ✅ **Reglas de negocio**
- ✅ **Estados de la base de datos**

## Notas para Mantenimiento

### Al modificar los endpoints:
1. Actualizar tests correspondientes
2. Verificar que las validaciones sigan siendo correctas
3. Probar cambios en reglas de negocio

### Al agregar nuevas funcionalidades:
1. Agregar tests para nuevos casos de uso
2. Mantener coherencia con el patrón existente
3. Documentar nuevas validaciones

### Debugging:
- Usar `-s` para ver prints: `pytest -s`
- Usar `--pdb` para debugging: `pytest --pdb`
- Ver logs de Django: Configurar logging en settings de test
