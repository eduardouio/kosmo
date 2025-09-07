from django.http import JsonResponse
from django.views import View
from common.StockDispoQuantity import StockDispoQuantity


class StockDetailAPI(View):
    def get(self, request, stock_day_id):
        # Usar la nueva clase StockDispoQuantity para obtener
        # el stock disponible
        stock_calculator = StockDispoQuantity(stock_day_id)
        result = stock_calculator.get_available_stock()
        
        # Si hay error, devolver el error
        if 'error' in result:
            return JsonResponse(
                {'error': result['error']},
                status=result['status']
            )
        
        # Si todo está bien, devolver el resultado completo
        return JsonResponse(result, status=200)
