import json
from django.views import View
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event


class CancelOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        loggin_event(f'CancelOrderAPI cancelada orden de compra {data}')
        order = Order.get_order_by_id(data)
        order.status = 'CANCELADO'
        order.save()
        self.validate_supplier_order(order.parent_order)
        return JsonResponse({'status': 'ok'})
    
    def validate_supplier_order(self, cus_order):
        loggin_event(f'CancelOrderAPI Validando ordenes {cus_order}')
        close_order = True
        all_sup_orders = Order.get_by_parent_order(cus_order)
        for sup_order in all_sup_orders:
            if sup_order.status != 'CONFIRMADO':
                close_order = False
                break           
