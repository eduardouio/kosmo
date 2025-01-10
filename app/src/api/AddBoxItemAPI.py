import json
from django.http import JsonResponse
from django.views.generic import View
from products.models import StockDetail, BoxItems, Product


class AddBoxItemAPI(View):
    def post(self, request, *args, **kwargs):
        request_data = json.loads(request.body)
        product = Product.get_by_id(request_data['product_id'])
        stock_detail = StockDetail.get_by_id(request_data['stock_detail_id'])
        if not product or not stock_detail:
            return JsonResponse({'message': 'Product or stock detail not found'}, status=404)

        box_item = BoxItems.objects.create(
            stock_detail=stock_detail,
            product=product,
            length=request_data['length'],
            qty_stem_flower=request_data['qty_stem_flower'],
            stem_cost_price=request_data['stem_cost_price'],
            profit_margin=request_data['margin']
        )
        StockDetail.rebuild_stock_detail(stock_detail)

        return JsonResponse(
            {
                'message': 'Item added to box',
                'box_item': {
                    'id': box_item.id,
                }
            },
            status=201
        )
