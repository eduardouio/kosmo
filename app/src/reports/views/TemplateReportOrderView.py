from django.views.generic import TemplateView
from trade.models import Order, OrderItems, OrderBoxItems
from datetime import datetime


class TemplateReportOrderView(TemplateView):
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
            'varieties': [],
        }

        for item in order_items_det:
            totals['total_hb'] += item['item'].quantity if item['item'].box_model == 'HB' else 0
            totals['total_qb'] += item['item'].quantity if item['item'].box_model == 'QB' else 0
            totals['total_stems'] += item['item'].tot_stem_flower
            for box_item in item['box_items']:
                if box_item.product.variety not in totals['varieties']:
                    totals['varieties'].append(box_item.product.variety)

        totals['total_fb'] = totals['total_qb'] // 4 + totals['total_hb'] // 2

        return totals
