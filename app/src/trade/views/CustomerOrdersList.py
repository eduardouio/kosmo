from django.views.generic import ListView
from trade.models import Order


class CustomerOrdersList(ListView):
    model = Order
    template_name = 'lists/customer_orders_list.html'
    context_object_name = 'orders'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Órdenes de Clientes'
        context['title_page'] = 'Órdenes de Clientes'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Orden eliminada exitosamente'
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            type_document='ORD_VENTA',
        ).order_by('-date')
