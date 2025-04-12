import json
from django.http import JsonResponse
from django.views import View
from common import SyncOrders
from common.AppLoger import loggin_event
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import Product


class UpdateSupplierOrderAPI(View):
    def post(self, request):
        loggin_event('Actualizando orden de proveedor')
        order_data = json.loads(request.body)
        my_order = Order.objects.get(id=order_data['order']['id'])

        if my_order.type_document != 'ORD_COMPRA':
            return JsonResponse(
                {
                    'error':
                    'No se puede modificar una orden de venta por este medio'
                },
                status=400
            )

        Order.disable_order_items(my_order)
        self.create_order_item(order_data['order_details'], my_order)
        Order.rebuild_totals(my_order)
        SyncOrders().sync_customer(my_order)

        return JsonResponse(
            {'message': 'actualizado con exito'}, status=201
        )

    def create_order_item(self, order_dertails, my_order):
        loggin_event(f'Creando los items nuevamente {my_order.pk}')

        for ord_item in order_dertails:
            new_ord_det = OrderItems.objects.create(
                order=my_order,
                id_stock_detail=ord_item['id_stock_detail'],
                line_price=ord_item['line_price'],
                line_margin=ord_item['line_margin'],
                line_total=ord_item['line_total'],
                tot_stem_flower=ord_item['tot_stem_flower'],
                box_model=ord_item['box_model'],
                quantity=ord_item['quantity']
            )

            self.create_box_items(ord_item['box_items'], new_ord_det)
        return True

    def create_box_items(self, box_items, ord_item):
        loggin_event(f'Actualizando cajas de la orden {ord_item.pk}')
        for new_bx_item in box_items:
            OrderBoxItems.objects.create(
                order_item=ord_item,
                product=Product.get_by_id(new_bx_item['product_id']),
                length=new_bx_item['length'],
                qty_stem_flower=new_bx_item['qty_stem_flower'],
                stem_cost_price=new_bx_item['stem_cost_price'],
                profit_margin=new_bx_item['margin']
            )

        return True
