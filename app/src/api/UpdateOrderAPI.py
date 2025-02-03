import json
from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems, OrderBoxItems
from common import SerializerOrder
from partners.models import Contact


class UpdateOrderAPI(View):
    def post(self, request):
        order_data = json.loads(request.body)
        order_items = order_data['order_details']
        import ipdb; ipdb.set_trace()

        for item in order_items:
            order_detail = OrderItems.get_by_id(item['id'])
            order_detail.qty_stem_flower = item['qty_stem_flower']
            order_detail.stem_cost_price = item['stem_cost_price']
            order_detail.profit_margin = item['profit_margin']
            order_detail.box_model = item['box_model']
            order_detail.tot_stem_flower = item['tot_stem_flower']
            order_detail.tot_cost_price_box = item['tot_cost_price_box']
            order_detail.save()