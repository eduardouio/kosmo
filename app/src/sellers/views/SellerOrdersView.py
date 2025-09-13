from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from trade.models import Order
from common.AppLoger import loggin_event


class SellerOrdersView(LoginRequiredMixin, ListView):
    """Vista para listar órdenes de venta del vendedor"""
    model = Order
    template_name = 'seller/orders_seller.html'
    context_object_name = 'orders'
    paginate_by = 15
    
    def get_queryset(self):
        """Filtrar órdenes de venta del usuario actual"""
        try:
            queryset = Order.objects.filter(
                type_document='ORD_VENTA',
                is_active=True
            ).select_related('partner', 'stock_day').order_by('-date')
            
            # Filtro por estado si se especifica
            status = self.request.GET.get('status')
            if status:
                queryset = queryset.filter(status=status)
            
            # Filtro por búsqueda
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    Q(consecutive__icontains=search) |
                    Q(partner__name__icontains=search) |
                    Q(num_order__icontains=search)
                )
            
            return queryset
            
        except Exception as e:
            loggin_event(f'Error obteniendo órdenes: {e}')
            return Order.objects.none()
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = 'Órdenes de Venta'
        
        # Estados disponibles para filtro
        ctx['status_choices'] = [
            ('PENDIENTE', 'Pendiente'),
            ('CONFIRMADO', 'Confirmado'),
            ('MODIFICADO', 'Modificado'),
            ('FACTURADO', 'Facturado'),
            ('CANCELADO', 'Cancelado'),
            ('PROMESA', 'Promesa')
        ]
        
        # Filtros activos
        ctx['current_status'] = self.request.GET.get('status', '')
        ctx['current_search'] = self.request.GET.get('search', '')
        
        # Estadísticas rápidas
        all_orders = self.get_queryset()
        ctx['total_orders'] = all_orders.count()
        ctx['total_amount'] = sum(order.total_price for order in all_orders)
        ctx['total_stems'] = sum(
            order.total_stem_flower or 0 for order in all_orders
        )
        
        return ctx
