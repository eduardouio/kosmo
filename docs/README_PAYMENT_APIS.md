# Payment APIs Documentation

## Endpoints de Pagos

Los siguientes endpoints permiten crear, actualizar y eliminar pagos en el sistema. Una factura puede tener varios pagos y un pago puede ser aplicado a más de una factura de forma total o parcial.

### 1. PaymentCreateUpdateAPI

#### Crear un nuevo pago
- **URL**: `POST /api/payments/`
- **Descripción**: Crea un nuevo pago que puede aplicarse a una o más facturas

**Estructura del JSON de entrada:**
```json
{
    "date": "2025-07-29",
    "due_date": "2025-08-29",  // Opcional
    "type_transaction": "INGRESO",  // Opcional, por defecto "INGRESO"
    "amount": "1500.00",
    "method": "TRANSF",  // TRANSF, CHEQUE, EFECTIVO, OTRO, TC, TD, NC
    "status": "PENDIENTE",  // Opcional, por defecto "PENDIENTE"
    "bank": "BANCO PICHINCHA",  // Requerido para TRANSF, TC, TD
    "nro_account": "123456789",  // Opcional
    "nro_operation": "OP123456789",  // Requerido para TRANSF, TC, TD
    "processed_by_id": 1,  // Opcional
    "approved_by_id": null,  // Opcional
    "approval_date": null,  // Opcional
    "invoices": [
        {
            "invoice_id": 1,
            "amount": "1000.00"
        },
        {
            "invoice_id": 2,
            "amount": "500.00"
        }
    ]
}
```

**Respuesta exitosa (201):**
```json
{
    "message": "Payment created successfully",
    "payment_id": 1,
    "payment_number": "PAY-000001"
}
```

#### Actualizar un pago existente
- **URL**: `PUT /api/payments/<payment_id>/`
- **Descripción**: Actualiza un pago existente (solo si está en estado PENDIENTE)

**Estructura del JSON de entrada:**
```json
{
    "date": "2025-07-30",
    "amount": "1600.00",
    "method": "EFECTIVO",
    "status": "CONFIRMADO",
    "invoices": [
        {
            "invoice_id": 1,
            "amount": "1100.00"
        },
        {
            "invoice_id": 2,
            "amount": "500.00"
        }
    ]
}
```

**Respuesta exitosa (200):**
```json
{
    "message": "Payment updated successfully",
    "payment_id": 1,
    "payment_number": "PAY-000001"
}
```

#### Obtener información de un pago
- **URL**: `GET /api/payments/<payment_id>/`
- **Descripción**: Obtiene los detalles de un pago específico

**Respuesta exitosa (200):**
```json
{
    "id": 1,
    "payment_number": "PAY-000001",
    "date": "2025-07-29",
    "due_date": "2025-08-29",
    "type_transaction": "INGRESO",
    "amount": "1500.00",
    "method": "TRANSF",
    "status": "PENDIENTE",
    "bank": "BANCO PICHINCHA",
    "nro_account": "123456789",
    "nro_operation": "OP123456789",
    "processed_by_id": 1,
    "approved_by_id": null,
    "approval_date": null,
    "invoices": [
        {
            "invoice_id": 1,
            "invoice_number": "FAC-001",
            "amount": "1000.00"
        },
        {
            "invoice_id": 2,
            "invoice_number": "FAC-002",
            "amount": "500.00"
        }
    ]
}
```

#### Listar pagos con paginación
- **URL**: `GET /api/payments/?page=1&page_size=20`
- **Descripción**: Lista los pagos con paginación básica

**Respuesta exitosa (200):**
```json
{
    "payments": [
        {
            "id": 1,
            "payment_number": "PAY-000001",
            "date": "2025-07-29",
            "amount": "1500.00",
            "method": "TRANSF",
            "status": "PENDIENTE",
            "total_invoices": 2
        }
    ],
    "page": 1,
    "page_size": 20
}
```

### 2. PaymentDeleteAPI

#### Eliminar múltiples pagos (Soft Delete)
- **URL**: `POST /api/payments/delete/`
- **Descripción**: Elimina (desactiva) múltiples pagos mediante soft delete

**Estructura del JSON de entrada:**
```json
{
    "payment_ids": [1, 2, 3]
}
```

**Respuesta exitosa (200, 207, o 400):**
```json
{
    "message": "2 payments deleted successfully",
    "deleted_payments": [
        {
            "id": 1,
            "payment_number": "PAY-000001"
        },
        {
            "id": 2,
            "payment_number": "PAY-000002"
        }
    ],
    "not_found_payments": [3],
    "cannot_delete_payments": []
}
```

#### Eliminar un pago específico
- **URL**: `DELETE /api/payments/<payment_id>/delete/`
- **Descripción**: Elimina (desactiva) un pago específico

**Respuesta exitosa (200):**
```json
{
    "message": "Payment deleted successfully",
    "payment_id": 1,
    "payment_number": "PAY-000001"
}
```

## Validaciones y Reglas de Negocio

### Crear/Actualizar Pagos:
1. **Campos requeridos**: `date`, `amount`, `method`, `invoices`
2. **Monto**: Debe ser mayor a cero
3. **Facturas**: Debe incluir al menos una factura
4. **Suma de montos**: El monto total del pago debe coincidir con la suma de los montos de las facturas
5. **Métodos de pago**: Para TRANSF, TC, TD se requiere banco y número de operación
6. **Fecha de vencimiento**: No puede ser anterior a la fecha de pago

### Eliminar Pagos:
1. **Estados no eliminables**: No se pueden eliminar pagos con estado CONFIRMADO o RECHAZADO
2. **Soft delete**: Los pagos se desactivan (is_active = False) en lugar de eliminarse físicamente
3. **Detalles asociados**: Al eliminar un pago, también se desactivan sus PaymentDetail asociados

## Códigos de Estado HTTP

- **200**: Operación exitosa
- **201**: Recurso creado exitosamente
- **207**: Operación parcialmente exitosa (algunos elementos procesados)
- **400**: Error en la solicitud (datos inválidos, validaciones fallidas)
- **404**: Recurso no encontrado
- **500**: Error interno del servidor

## Ejemplo de Uso Completo

```bash
# 1. Crear un pago que se aplica a dos facturas
curl -X POST http://localhost:8000/api/payments/ \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-07-29",
    "amount": "1500.00",
    "method": "TRANSF",
    "bank": "BANCO PICHINCHA",
    "nro_operation": "OP123456789",
    "invoices": [
      {"invoice_id": 1, "amount": "1000.00"},
      {"invoice_id": 2, "amount": "500.00"}
    ]
  }'

# 2. Actualizar el pago
curl -X PUT http://localhost:8000/api/payments/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "1600.00",
    "status": "CONFIRMADO",
    "invoices": [
      {"invoice_id": 1, "amount": "1100.00"},
      {"invoice_id": 2, "amount": "500.00"}
    ]
  }'

# 3. Obtener información del pago
curl -X GET http://localhost:8000/api/payments/1/

# 4. Eliminar el pago
curl -X DELETE http://localhost:8000/api/payments/1/delete/
```
