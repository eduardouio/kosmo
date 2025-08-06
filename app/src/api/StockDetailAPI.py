from django.http import JsonResponse
from django.views import View
from products.models import StockDay, StockDetail
from common.SerializerStock import SerializerStock

MESSAGE = 'No hay detalles para esta diponibilidad, debe importar primero'


class StockDetailAPI(View):
    def get(self, request, stock_day_id):
        stock_day = StockDay.get_by_id(stock_day_id)
        if not stock_day:
            return JsonResponse({'error': MESSAGE}, status=404)

        stock_details = StockDetail.get_by_stock_day(stock_day)
        if not stock_details:
            return JsonResponse({'error': MESSAGE}, status=404)

        result_dict = []

        for stock in stock_details:
            result_dict.append(SerializerStock().get_line(stock))

        stock_day = StockDay.get_by_id(stock_day_id)
        orders = []
        return JsonResponse(
            {
                'stock': result_dict,
                'stockDay': {
                    'id': stock_day.id,
                    'date': stock_day.date,
                    'is_active': stock_day.is_active,
                },
                'orders': [o.id for o in orders],
            },
            status=200
        )
