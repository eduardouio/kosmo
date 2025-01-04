import json
from django.http import JsonResponse
from django.views import View
from products.models import StockDetail, BoxItems


class UpdateStockDetailAPI(View):
    def post(self, request):
        data = json.loads(request.body)
        box_item = BoxItems.get_by_id(data['id'])
        if not box_item:
            return JsonResponse(
                {
                    'error': 'Box item not found'
                },
                status=404
            )

        box_item.qty_stem_flower = data['qty_stem_flower']
        box_item.stem_cost_price = data['stem_cost_price']
        box_item.profit_margin = data['profit_margin']
        box_item.save()
        StockDetail.rebuild_stock_detail(box_item.stock_detail)
        return JsonResponse(
            {
                'message': 'Stock detail updated'
            },
            status=200
        )
