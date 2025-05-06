import json
from django.views import View
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event


class AprovePurchaseOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        loggin_event(f'AproveOrderAPI confirmado orden de compra {data}')
        order = Order.get_order_by_id(data)
        order.status = 'CONFIRMADO'
        order.save()
        if order.type_document == 'ORD_COMPRA':
            self.validate_supplier_order(cus_order=order.parent_order)
        else:
            self.aprove_sup_order(order)

        return JsonResponse({'status': 'ok'})

    def validate_supplier_order(self, cus_order):
        loggin_event(f'AproveOrderAPI Validando ordenes hermanas {cus_order}')
        all_confirmed = True
        all_sup_orders = Order.get_by_parent_order(cus_order)
        for sup_order in all_sup_orders:
            if sup_order.status in ['PENDIENTE', 'MODIFICADO']:
                all_confirmed = False
                break

        if all_confirmed:
            loggin_event(
                f'AproveOrderAPI confirmando orden de compra {cus_order}'
            )
            cus_order.status = 'CONFIRMADO'
            cus_order.save()

    def aprove_sup_order(self, order):
        loggin_event(f'AproveOrderAPI Aprobando orden de compra {order}')
        order.status = 'CONFIRMADO'
        order.save()
        sup_order = Order.get_by_parent_order(order)
        for order in sup_order:
            order.status = 'CONFIRMADO'
            order.save()

        return order
