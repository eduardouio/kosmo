# Mejoras en Tablas de Balance Financiero

## Cambios Realizados

### 1. **Cálculos de FB Equivalente**

Se agregó el cálculo automático de FB equivalente usando las fórmulas de conversión:
- **HB = 1FB/2** → `HB ÷ 2 = FB`
- **QB = 1FB/4** → `QB ÷ 4 = FB`  
- **EB = 1FB/8** → `EB ÷ 8 = FB`

**Fórmula implementada:**
```python
fb_equivalente = total_fb + (total_hb / 2) + (total_qb / 4) + (total_eb / 8)
```

### 2. **Nuevas Columnas en Backend**

Se agregaron campos adicionales a las consultas:

#### Compras por Proveedor:
```python
compras_por_proveedor = purchase_invoices.values('partner__name').annotate(
    total=Sum('total_price'),
    count=Count('id'),
    total_eb=Sum('eb_total'),      # Nuevas columnas
    total_hb=Sum('hb_total'),      # Nuevas columnas
    total_qb=Sum('qb_total'),      # Nuevas columnas
    total_fb=Sum('fb_total'),      # Nuevas columnas
    total_tallos=Sum('tot_stem_flower')  # Nuevas columnas
)
```

#### Ventas por Cliente:
```python
ventas_por_cliente = sales_invoices.values('partner__name').annotate(
    total=Sum('total_price'),
    margin=Sum('total_margin'),
    count=Count('id'),
    total_eb=Sum('eb_total'),      # Nuevas columnas
    total_hb=Sum('hb_total'),      # Nuevas columnas  
    total_qb=Sum('qb_total'),      # Nuevas columnas
    total_fb=Sum('fb_total'),      # Nuevas columnas
    total_tallos=Sum('tot_stem_flower')  # Nuevas columnas
)
```

### 3. **Tablas Scrolleables de Tamaño Fijo**

#### CSS Implementado:
```css
.scrollable-table-card {
    height: 400px;  /* Altura fija para todas las cards */
}

.scrollable-table-card .card-body {
    padding: 0;
    height: 350px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    position: relative;
    padding-bottom: 40px;
}

.scrollable-table-card .table-responsive {
    flex: 1;
    overflow-y: auto;  /* Scroll vertical automático */
    font-size: 0.8rem;
}

.scrollable-table-card .table th {
    position: sticky;  /* Encabezados fijos al hacer scroll */
    top: 0;
    background-color: #f8f9fa;
    z-index: 10;
}
```

### 4. **Nuevas Columnas en las Tablas HTML**

#### Tabla de Proveedores (Compras):
| Proveedor | Qty | FB Equiv | Tallos | EB | HB | QB | FB | Monto |
|-----------|-----|----------|--------|----|----|----|----|-------|

#### Tabla de Clientes (Ventas):
| Cliente | Qty | FB Equiv | Tallos | EB | HB | QB | FB | Margen | Total |
|---------|-----|----------|--------|----|----|----|----|--------|-------|

### 5. **Mejoras Visuales**

- **Tablas con rayas**: `table-striped` para mejor lectura
- **Tooltips**: `title` attribute para nombres completos
- **Headers colorados**: Verde para ingresos, rojo para egresos
- **Números compactos**: `floatformat:0` para mostrar sin decimales
- **Scroll suave**: Todas las tablas tienen la misma altura y scroll independiente

### 6. **Responsive Design**

```css
@media (max-width: 768px) {
    .scrollable-table-card {
        height: 300px;  /* Altura reducida en móviles */
    }
    .scrollable-table-card .card-body {
        height: 250px;
    }
}
```

## Archivos Modificados

### 1. **`BalanceReportView.py`**
- ✅ Agregadas consultas para totales de cajas (EB, HB, QB, FB)
- ✅ Agregadas consultas para total de tallos
- ✅ Implementado cálculo automático de FB equivalente
- ✅ Aumentado límite de registros de 10 a 15

### 2. **`balance_report.html`**
- ✅ Agregados estilos CSS para tablas scrolleables
- ✅ Nuevas columnas en tabla de proveedores (9 columnas)
- ✅ Nuevas columnas en tabla de clientes (10 columnas)
- ✅ Headers coloreados para tablas de flujo
- ✅ Totales fijos en la parte inferior
- ✅ Tooltips para nombres completos

## Beneficios

### 📊 **Más Información**
- Vista completa de tipos de cajas por proveedor/cliente
- Cálculo automático de equivalencias FB
- Total de tallos por transacción

### 🎨 **Mejor UX**
- Tablas de tamaño uniforme (400px altura)
- Scroll independiente para cada tabla
- Encabezados fijos al hacer scroll
- Headers colorados por tipo de transacción

### 📱 **Responsive**
- Adaptación automática a dispositivos móviles
- Texto más pequeño pero legible
- Tooltips para información completa

### 📈 **Análisis Mejorado**
- Comparación directa de FB equivalente
- Visualización de distribución de tipos de caja
- Métricas de volumen (tallos) vs valor (monto)

## Conversiones FB Implementadas

| Tipo Caja | Conversión a FB | Ejemplo |
|-----------|-----------------|---------|
| EB        | EB ÷ 8         | 80 EB = 10 FB |
| QB        | QB ÷ 4         | 40 QB = 10 FB |
| HB        | HB ÷ 2         | 20 HB = 10 FB |
| FB        | FB × 1         | 10 FB = 10 FB |

**Resultado:** FB Equivalente Total = 40 FB en este ejemplo.