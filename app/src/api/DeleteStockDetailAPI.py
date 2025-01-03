import json
from django.http import JsonResponse
from django.views import View
from products.models import StockDetail


class DeleteStockDetailAPI(View):
    def post(self, request):
        stk_detail = json.loads(request.body)
        for stock_detail in stk_detail:
            stock_detail = StockDetail.get_by_id(
                stock_detail['stock_detail_id'])
            if not stock_detail:
                continue

            stock_detail.is_active = False
            stock_detail.save()

        return JsonResponse(
            {
                'message': 'Stock detail deleted'
            },
            status=200
        )
