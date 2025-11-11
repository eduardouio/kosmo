from django.views.generic import ListView
from trade.models import Order
from django.db.models import Sum
from datetime import datetime


# trade/customer-orders/
class CustomerOrdersList(ListView):
    model = Order
    template_name = 'lists/customer_orders_list.html'
    context_object_name = 'orders'
    ordering = ['-created_at']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Órdenes de Clientes'
        context['title_page'] = 'Órdenes de Clientes'
        context['action'] = None

        # Agregar estadísticas de ventas
        context['por_confirmar'] = self.get_por_confirmar()
        context['ventas_facturadas'] = self.get_ventas_facturadas()
        context['tallos_confirmados'] = self.get_tallos_confirmados()
        context['tallos_facturados'] = self.get_tallos_facturados()
        context['ventas_mes'] = self.get_ventas_mes()
        context['facturado_mes'] = self.get_facturado_mes()

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Orden eliminada exitosamente'
        return context

    def get_por_confirmar(self):
        """Valor en dolares de Órdenes de venta sin factura en estado modificado y confirmado"""
        return Order.objects.filter(
            type_document='ORD_VENTA',
            status__in=['MODIFICADO', 'CONFIRMADO'],
            is_invoiced=False,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_ventas_facturadas(self):
        """El total de órdenes de venta que han sido facturadas"""
        return Order.objects.filter(
            type_document='ORD_VENTA',
            is_invoiced=True,
            is_active=True
        ).count()

    def get_tallos_confirmados(self):
        """Total de tallos de los pedidos de venta que están confirmados"""
        return Order.objects.filter(
            type_document='ORD_VENTA',
            status='CONFIRMADO',
            is_active=True
        ).aggregate(total=Sum('total_stem_flower'))['total'] or 0

    def get_tallos_facturados(self):
        """Total de tallos de los pedidos de venta que tienen factura"""
        return Order.objects.filter(
            type_document='ORD_VENTA',
            is_invoiced=True,
            is_active=True
        ).aggregate(total=Sum('total_stem_flower'))['total'] or 0

    def get_ventas_mes(self):
        """Valor total de órdenes de venta por mes"""
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_VENTA',
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_facturado_mes(self):
        """Valor total facturado por mes para ventas"""
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_VENTA',
            is_invoiced=True,
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            type_document='ORD_VENTA',
        ).order_by('-created_at')
        
        # Agregar órdenes de compra relacionadas a cada orden de venta
        for order in queryset:
            order.related_purchase_orders = Order.get_by_parent_order(order)
        
        return queryset
