import json
from django.views import View
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event
from trade.models import OrderBoxItems, OrderItems
from products.models import StockDetail


class CancelSupplierOrderAPI(View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        loggin_event(
            f'CancelSupplierOrderAPI cancelada orden de compra {data}')
        order = Order.get_order_by_id(data['id_order'])
        if order.status in ['FACTURADO', 'CANCELADO']:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'La orden no se puede cancelar, se ecuentra en estado de facturada o cancelada'
                }
            )
        if order.parent_order in ['FACTURADO', 'CANCELADO']:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'La orden no se puede cancelar, la orden de venta es cancelada o facturada'
                }
            )

        self.update_customer_order(
            cus_order=order.parent_order, id_supplier=order.partner.id
        )
        order.status = 'CANCELADO'
        order.save()
        return JsonResponse(
            {'status': 'ok'}
        )

    def update_customer_order(self, cus_order,  id_supplier):
        loggin_event(f'Actualizando los items de la ordern de compra')
        cus_order_items = OrderItems.get_by_order(cus_order)
        for coi in cus_order_items:
            stock_detail = StockDetail.get_by_id(coi.id_stock_detail)
            if stock_detail.partner.id == id_supplier:
                OrderItems.disable_by_order_item(coi)

        all_confirmed = True
        
        all_sup_orders = Order.get_by_parent_order(cus_order)
        for sup_order in all_sup_orders:
            if sup_order.status in ['PENDIENTE', 'MODIFICADO']:
                all_confirmed = False
                break
        
        Order.rebuild_totals(cus_order)

        # Verificamos el status de la orden
        if all_confirmed:
            loggin_event(
                f'AproveOrderAPI confirmando orden de compra {cus_order}'
            )
            cus_order.status = 'CONFIRMADO'
            cus_order.save()
            return True
        
        cus_order.status = 'MODIFICADO'
        cus_order.save()
