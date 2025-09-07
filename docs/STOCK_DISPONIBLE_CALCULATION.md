# StockDispoQuantity - Análisis de Stock Disponible

## Descripción

La clase `StockDispoQuantity` analiza el stock inicial disponible de productos y le resta las cantidades que ya han sido asignadas a órdenes activas, proporcionando una vista precisa del inventario disponible para nuevos pedidos.

## Características

### Exclusiones Automáticas
- ❌ Órdenes con estado "CANCELADO"
- ❌ Órdenes con `is_active = False`
- ❌ Órdenes que cumplan ambas condiciones

### Estados Considerados
- ✅ PENDIENTE
- ✅ CONFIRMADO
- ✅ MODIFICADO
- ✅ FACTURADO
- ✅ PROMESA

## Compatibilidad

La salida de `StockDispoQuantity` es **100% compatible** con la vista `StockDetailAPI` existente. Solo se modifican las cantidades disponibles, manteniendo toda la estructura de datos original.

## Uso

### Implementación Básica
```python
from common.StockDispoQuantity import StockDispoQuantity

# Crear instancia
calculator = StockDispoQuantity(stock_day_id)

# Obtener stock disponible
result = calculator.get_available_stock()

if 'error' not in result:
    # Procesar datos de stock disponible
    stock_items = result['stock']
    stock_day_info = result['stockDay']
    related_orders = result['orders']
```

### En StockDetailAPI
```python
# La API ha sido actualizada para usar automáticamente StockDispoQuantity
# No se requieren cambios en el frontend
GET /api/stock_detail/{stock_day_id}/
```

## Estructura de Respuesta

```json
{
  "stock": [
    {
      "stock_detail_id": 123,
      "quantity": 15,          // Cantidad disponible (original - asignada)
      "is_in_order": true,     // Indica si hay órdenes usando este stock
      "partner": { ... },
      "box_items": [
        {
          "id": 456,
          "qty_stem_flower": 48  // Cantidad disponible por box_item
        }
      ]
    }
  ],
  "stockDay": {
    "id": 1,
    "date": "2025-09-07",
    "is_active": true
  },
  "orders": [101, 102, 103],   // IDs de órdenes relacionadas activas
  "status": 200
}
```

## Lógica de Cálculo

### Cantidades de Cajas
1. Busca todas las `OrderItems` que referencian cada `StockDetail`
2. Filtra solo órdenes activas y con estados válidos
3. Suma las cantidades de cajas asignadas
4. Resta del stock original: `disponible = original - asignado`

### Cantidades de Box Items
1. Por cada `OrderBoxItems` en las órdenes activas
2. Encuentra el `BoxItem` original correspondiente (por `product_id` y `length`)
3. Calcula: `asignado = qty_stem_flower * cantidad_cajas_orden`
4. Resta del stock original: `disponible = original - asignado`

### Indicadores
- `is_in_order`: Se marca como `true` si hay cantidades asignadas
- `quantity`: Nunca puede ser negativa (se usa `max(0, original - asignado)`)

## Archivos Modificados

- ✅ `/common/StockDispoQuantity.py` - Nueva clase principal
- ✅ `/api/StockDetailAPI.py` - Actualizada para usar la nueva funcionalidad
- ✅ `/test_stock_quantity.py` - Script de pruebas

## Pruebas

Para probar la funcionalidad:

```bash
cd /Users/eduardo/Repositorios/kosmo/app/src
python test_stock_quantity.py
```

## Notas Técnicas

- La clase mantiene toda la lógica del `SerializerStock` original
- Se preserva la compatibilidad con el frontend existente
- Los cálculos se realizan en tiempo real para mayor precisión
- Se optimiza evitando cálculos innecesarios cuando no hay órdenes
