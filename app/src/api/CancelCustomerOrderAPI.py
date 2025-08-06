import json
from django.views import View
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event
from common.SyncOrders import SyncOrders


class CancelCustomerOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        loggin_event(f'CancelOrderAPI cancelada orden de venta {data}')
        order = Order.get_order_by_id(data['id_order'])
        if order.status in ['FACTURADO', 'CANCELADO']:
            return JsonResponse({
                'status': 'error',
                'message': 'La orden de venta no se puede cancelar'
            })
        loggin_event(f'Cancelando orden de compra de la SO {order.id}')
        SyncOrders().cancell_supplier_orders(order)
        order.status = 'CANCELADO'
        order.save()
        return JsonResponse(
            {'status': 'ok'}
        )
