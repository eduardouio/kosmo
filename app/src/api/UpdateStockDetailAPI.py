import json
from django.http import JsonResponse
from django.views import View
from products.models import StockDetail, BoxItems


class UpdateStockDetailAPI(View):
    def post(self, request):
        data = json.loads(request.body)

        for box in data:
            box_item = BoxItems.get_by_id(box['id'])
            box_item.qty_stem_flower = box['qty_stem_flower']
            box_item.stem_cost_price = box['stem_cost_price']
            box_item.profit_margin = box['margin']
            box_item.is_active = box['is_active']
            box_item.save()
            StockDetail.rebuild_stock_detail(box_item.stock_detail)
        return JsonResponse(
            {
                'message': 'Stock detail updated'
            },
            status=200
        )
