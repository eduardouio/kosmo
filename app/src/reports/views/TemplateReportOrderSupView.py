from django.views.generic import TemplateView
from trade.models import Order, OrderItems, OrderBoxItems
from datetime import datetime
from accounts.models.CustomUserModel import CustomUserModel


class TemplateReportOrderSupView(TemplateView):
    template_name = 'reports/order_supplier.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = kwargs.get('id_order')
        order = Order.objects.get(pk=order)
        Order.rebuild_totals(order)
        order_items = OrderItems.get_by_order(order)
        order_items_det = []
        for item in order_items:
            box_items = OrderBoxItems.get_by_order_item(item)
            box_items_with_totals = []
            for box_item in box_items:
                box_items_with_totals.append({
                    'box_item': box_item,
                    'total_stems': box_item.qty_stem_flower * item.quantity
                })
            order_items_det.append({
                'item': item,
                'box_items': box_items_with_totals
            })
        context['order'] = order
        context['order_items'] = order_items_det
        # validamos por si el usuario creador del pedido no existe
        id_user_created = order.id_user_created if order.id_user_created else 1
        context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
        context['now'] = datetime.now()
        return context