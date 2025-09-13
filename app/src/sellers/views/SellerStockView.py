from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from products.models import StockDay, StockDetail, BoxItems
from common.AppLoger import loggin_event


class SellerStockView(LoginRequiredMixin, ListView):
    """Vista para mostrar stocks disponibles"""
    template_name = 'seller/stocks_seller.html'
    context_object_name = 'stock_items'
    paginate_by = None  # Deshabilitamos paginación del servidor
    
    def get_queryset(self):
        """Obtener stocks activos más recientes con filtros"""
        try:
            # Obtener el último stock day activo
            latest_stock_day = StockDay.objects.filter(
                is_active=True
            ).order_by('-date').first()
            
            if latest_stock_day:
                queryset = StockDetail.objects.filter(
                    stock_day=latest_stock_day,
                    is_active=True
                ).select_related(
                    'partner', 'stock_day'
                ).prefetch_related(
                    'boxitems_set__product'
                ).order_by('partner__name')
                
                # Filtro por búsqueda de variedad
                search = self.request.GET.get('search')
                if search:
                    queryset = queryset.filter(
                        Q(partner__name__icontains=search) |
                        Q(partner__short_name__icontains=search) |
                        Q(boxitems__product__name__icontains=search) |
                        Q(box_model__icontains=search)
                    ).distinct()
                
                return queryset
            return StockDetail.objects.none()
        except Exception as e:
            loggin_event(f'Error obteniendo stocks: {e}')
            return StockDetail.objects.none()
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = 'Disponibilidades - Stock'
        
        # Filtros activos
        ctx['current_search'] = self.request.GET.get('search', '')
        
        # Obtener información del stock day actual
        latest_stock_day = StockDay.objects.filter(
            is_active=True
        ).order_by('-date').first()
        ctx['current_stock_day'] = latest_stock_day
        
        # Calcular totales
        stock_items = self.get_queryset()
        ctx['total_boxes'] = sum(item.quantity for item in stock_items)
        ctx['total_stems'] = sum(item.tot_stem_flower for item in stock_items)
        
        # Resumen por tipo de caja
        box_summary = {}
        for item in stock_items:
            box_type = item.box_model
            if box_type not in box_summary:
                box_summary[box_type] = {'quantity': 0, 'stems': 0}
            box_summary[box_type]['quantity'] += item.quantity
            box_summary[box_type]['stems'] += item.tot_stem_flower
        
        ctx['box_summary'] = box_summary
        
        # Preparar datos para JavaScript (sin filtros para tener todos los datos)
        all_stock_items = StockDetail.objects.filter(
            stock_day=latest_stock_day,
            is_active=True
        ).select_related(
            'partner', 'stock_day'
        ).prefetch_related(
            'boxitems_set__product'
        ).order_by('partner__name') if latest_stock_day else []
        
        # Serializar datos para JS
        import json
        stock_data = []
        for item in all_stock_items:
            varieties = []
            for box_item in item.boxitems_set.all():
                varieties.append({
                    'id': box_item.id,
                    'product_name': box_item.product.name,
                    'length': box_item.length,
                    'qty_stem_flower': box_item.qty_stem_flower,
                    'stem_cost_price': float(box_item.stem_cost_price),
                    'profit_margin': float(box_item.profit_margin),
                    'total_bunches': box_item.total_bunches or 0,
                    'stems_bunch': box_item.stems_bunch or 0,
                })
            
            stock_data.append({
                'id': item.id,
                'partner_name': item.partner.name,
                'partner_short_name': item.partner.short_name or item.partner.name,
                'box_model': item.box_model,
                'quantity': item.quantity,
                'tot_stem_flower': item.tot_stem_flower,
                'tot_cost_price_box': float(item.tot_cost_price_box),
                'profit_margin': float(item.profit_margin),
                'varieties': varieties,
            })
        
        ctx['stock_data_json'] = json.dumps(stock_data)
        return ctx
