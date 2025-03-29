from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Order, OrderItems, OrderBoxItems


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'presentations/order_presentation.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title_section'] = f"Orden {self.object.num_order}"
        context['title_page'] = f"Orden {self.object.num_order}"
        context['order_items'] = OrderItems.get_by_order(self.object)
        context['box_items'] = OrderBoxItems.objects.filter(
            order_item__order=self.object, is_active=True
        )
        context['delivery_date'] = self.object.delivery_date
        context['status'] = self.object.status
        context['total_price'] = self.object.total_price
        context['total_margin'] = self.object.total_margin
        context['action'] = self.request.GET.get('action')

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        message = ''

        if context['action'] == 'created':
            message = 'La orden ha sido creada con éxito.'
        elif context['action'] == 'updated':
            message = 'La orden ha sido actualizada con éxito.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'
        elif context['action'] == 'deleted_related':
            message = 'El registro ha sido eliminado exitosamente.'

        context['message'] = message
        return context
