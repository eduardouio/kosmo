# Actualización Automática del Estado de Facturas

## Descripción del Problema

Anteriormente, cuando se registraban pagos o cobros, el estado de las facturas no se actualizaba automáticamente. Las facturas permanecían en estado `PENDIENTE` incluso cuando estaban completamente pagadas.

## Solución Implementada

Se ha implementado un sistema automático que:

1. **Actualiza el estado de las facturas automáticamente** cuando se crean, modifican o eliminan pagos
2. **Calcula el total pagado** de cada factura sumando todos los pagos confirmados
3. **Cambia el estado a `PAGADO`** cuando el total pagado ≥ total de la factura
4. **Mantiene el estado `PENDIENTE`** cuando aún hay saldo pendiente
5. **Respeta las facturas `ANULADAS`** (no las modifica)

## Nuevas Funcionalidades

### En el Modelo Invoice

#### Nuevas Propiedades:
- `total_paid`: Calcula el total pagado de la factura
- `is_fully_paid`: Verifica si la factura está completamente pagada
- `pending_amount`: Calcula el monto pendiente de pago

#### Nuevos Métodos:
- `update_payment_status()`: Actualiza el estado basado en los pagos
- `update_all_payment_statuses()`: Actualiza todas las facturas (método de clase)

### En el Modelo PaymentDetail

#### Comportamiento Automático:
- Al crear un `PaymentDetail`, se actualiza automáticamente el estado de la factura
- Al eliminar un `PaymentDetail`, se recalcula el estado de la factura
- Solo considera pagos con estado `CONFIRMADO`

### En el Modelo Payment

#### Comportamiento Automático:
- Al cambiar el estado de un `Payment`, se actualizan todas las facturas relacionadas

### En las APIs

#### PaymentCreateUpdateAPI y CollectionsCreateUpdateAPI:
- Después de crear pagos/cobros, se actualiza explícitamente el estado de las facturas

## Comando de Django

Se ha creado un comando para actualizar facturas existentes:

```bash
# Mostrar qué facturas se actualizarían (sin aplicar cambios)
python manage.py update_invoice_payment_status --dry-run

# Aplicar los cambios
python manage.py update_invoice_payment_status
```

## Ejemplos de Uso

### Escenario 1: Factura Completamente Pagada
```python
# Factura con total de $1000
invoice = Invoice.objects.get(id=123)
print(invoice.total_invoice)  # 1000.00
print(invoice.status)         # 'PENDIENTE'

# Se registra un pago de $1000
payment = Payment.objects.create(...)
PaymentDetail.objects.create(
    payment=payment,
    invoice=invoice,
    amount=1000.00
)

# El estado se actualiza automáticamente
invoice.refresh_from_db()
print(invoice.status)         # 'PAGADO'
print(invoice.is_fully_paid)  # True
```

### Escenario 2: Pago Parcial
```python
# Factura con total de $1000
invoice = Invoice.objects.get(id=123)
print(invoice.total_invoice)  # 1000.00

# Se registra un pago de $600
PaymentDetail.objects.create(
    payment=payment,
    invoice=invoice,
    amount=600.00
)

# El estado permanece pendiente
invoice.refresh_from_db()
print(invoice.status)          # 'PENDIENTE'
print(invoice.total_paid)      # 600.00
print(invoice.pending_amount)  # 400.00
print(invoice.is_fully_paid)   # False
```

### Escenario 3: Múltiples Pagos
```python
# Factura con total de $1000
invoice = Invoice.objects.get(id=123)

# Primer pago de $400
PaymentDetail.objects.create(payment=payment1, invoice=invoice, amount=400.00)
print(invoice.status)  # 'PENDIENTE'

# Segundo pago de $600
PaymentDetail.objects.create(payment=payment2, invoice=invoice, amount=600.00)
print(invoice.status)  # 'PAGADO' (400 + 600 = 1000)
```

## Consideraciones Importantes

1. **Solo pagos confirmados**: Solo se consideran pagos con `status='CONFIRMADO'`
2. **Facturas anuladas**: Las facturas con estado `ANULADO` no se modifican
3. **Pagos activos**: Solo se consideran `PaymentDetail` con `is_active=True`
4. **Actualización automática**: El sistema funciona automáticamente, no requiere intervención manual
5. **Logs**: Todos los cambios de estado se registran en los logs

## Migración de Datos Existentes

Para actualizar facturas que ya estaban en el sistema:

```bash
# 1. Revisar qué facturas se actualizarían
python manage.py update_invoice_payment_status --dry-run

# 2. Si todo se ve bien, aplicar los cambios
python manage.py update_invoice_payment_status
```

## Próximos Pasos

- [ ] Considerar notificaciones cuando una factura cambie a estado `PAGADO`
- [ ] Agregar reportes de facturas pagadas vs pendientes
- [ ] Implementar alertas para facturas vencidas no pagadas
