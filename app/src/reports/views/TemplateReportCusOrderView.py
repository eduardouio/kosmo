from django.views.generic import TemplateView
from trade.models import Order, OrderItems, OrderBoxItems
from datetime import datetime
from accounts.models.CustomUserModel import CustomUserModel


# http://localhost:8000/reports/order-customer-template/12/
class TemplateReportCusOrderView(TemplateView):
    template_name = 'reports/order_customer.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = kwargs.get('id_order')
        order = Order.objects.get(pk=order)
        order_items = OrderItems.get_by_order(order)
        order_items_det = []
        for item in order_items:
            order_items_det.append({ 
                'item': item,
                'box_items': OrderBoxItems.get_by_order_item(item)
            })
        context['order'] = order
        context['order_items'] = order_items_det
        context['totals'] = self.get_totals(order_items_det)
        # validamos por si el usuario creador del pedido no existe
        id_user_created = order.id_user_created if order.id_user_created else 1
        context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
        context['now'] = datetime.now()
        return context

    def get_totals(self, order_items_det):
        totals = {
            'total_hb': 0,
            'total_qb': 0,
            'total_fb': 0,
            'total_stems': 0,
            'total_boxes': 0,
            'pieces': len(order_items_det),
        }

        for item in order_items_det:
            totals['total_hb'] += item['item'].quantity if item['item'].box_model == 'HB' else 0
            totals['total_qb'] += item['item'].quantity if item['item'].box_model == 'QB' else 0
            totals['total_stems'] += item['item'].tot_stem_flower

        total_hb = totals['total_qb'] // 2 + totals['total_hb']
        totals['total_fb'] = total_hb // 2

        return totals
