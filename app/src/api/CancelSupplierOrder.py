import json
from django.views import View
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event
from common import SyncOrders


class CancelSupplierOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        loggin_event(
            f'CancelSupplierOrderAPI cancelada orden de compra {data}')
        order = Order.get_order_by_id(data)
        if order.status in ['FACTURADO', 'CANCELADO']:
            return JsonResponse(
                {'status': 'error', 'message': 'La orden no se puede cancelar'}
            )
        SyncOrders().sync_suppliers(order.parent_order)
        order.status = 'CANCELADO'
        order.save()
        return JsonResponse(
            {'status': 'ok'}
        )
