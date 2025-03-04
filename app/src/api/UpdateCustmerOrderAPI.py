import json
from django.http import JsonResponse
from django.views import View
from common import SyncOrders
from common import loggin
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import Product


class UpdateCustmerOrderAPI(View):
    def post(self, request):
        loggin('Actualizando orden de cliente')
        order_data = json.loads(request.body)
        my_order = Order.objects.get(id=order_data['order']['id'])

        if my_order.type_document != 'ORD_VENTA':
            return JsonResponse(
                {'error': 'No se puede modificar una orden de compra'},
                status=400
            )

        old_order_items = OrderItems.get_by_order(my_order.pk)

        for old_order_item in old_order_items:
            for new_order_item in order_data['order_items']:
                if new_order_item['order_item_id'] not in [i.pk for i in old_order_items]:
                    ord_itm = OrderItems.get_by_id(
                        new_order_item['order_item_id'])
                    ord_itm.is_active = False
                    ord_itm.save()

                if old_order_item.id == new_order_item['order_item_id']:
                    self.update_order_item(new_order_item, old_order_item)

            OrderItems.rebuild_order_item(new_order_item)
        Order.rebuild_totals(my_order)

        SyncOrders.sync(my_order)

        return JsonResponse(
            {'message': 'actualizado con exito'}, status=201
        )

    def update_order_item(self, new_order_item, old_order_item):
        loggin(f'Actualizando item de orden {old_order_items.id}')
        current_data = {
            'order_item_id': old_order_item.pk,
            'id_stock_detail': old_order_item.id_stock_detail,
            'quantity': old_order_item.quantity,
            'box_model': old_order_item.box_model,
            'line_price': old_order_item.line_price,
            'line_total': old_order_item.line_total,
        }
        new_data = {
            'order_item_id': new_order_item['order_item_id'],
            'id_stock_detail': new_order_item['id_stock_detail'],
            'quantity': new_order_item['quantity'],
            'box_model': new_order_item['box_model'],
            'line_price': new_order_item['line_price'],
            'line_total': new_order_item['line_total'],
        }

        if current_data != new_data:
            old_order_item.id_stock_detail = new_order_item['id_stock_detail']
            old_order_item.quantity = new_order_item['quantity']
            old_order_item.box_model = new_order_item['box_model']
            old_order_item.line_price = new_order_item['line_price']
            old_order_item.line_total = new_order_item['line_total']
            old_order_item.is_modified = True
            old_order_item.save()
            # actualizamos las cajas de la orden
            self.update_box_items(old_order_item, new_order_item)
            return True

    def update_box_items(self, old_order_item, new_order_item):
        loggin(f'Actualizando cajas de la orden {old_order_item.id}')
        OrderBoxItems.disable_by_order_items(old_order_item)

        for new_box_item in new_order_item['box_items']:
            OrderBoxItems.create(
                order_item=old_order_item,
                product=Product.get_by_id(new_box_item['product']),
                length=new_box_item['length'],
                qty_stem_flower=new_box_item['box_item'],
                stem_cost_price=new_box_item['quantity'],
                profit_margin=new_box_item['margin'],
            )

        return True
