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
                {'error': 'No se puede modificar una orden de venta por este medio'},
                status=400
            )

        old_order_items = OrderItems.get_by_order(my_order.pk)
        to_delete = []

        # desactivo las order_item que no estan en la nueva orden
        for new_order_item in order_data['order_details']:
            for old_order_item in old_order_items:
                if old_order_item.id not in [i['order_item_id'] for i in order_data['order_details']]:
                    loggin_event(
                        f'Desactivando item de orden {old_order_item.id}')
                    to_delete.append(old_order_item.id)
                    ord_itm = OrderItems.get_by_id(old_order_item.id)
                    ord_itm.is_active = False
                    ord_itm.save()
                    OrderBoxItems.disable_by_order_items(ord_itm)
                    continue

        purge_new_details = [
            i for i in old_order_items if i.id not in to_delete
        ]

        # actualizo los items de la orden
        for new_order_item in order_data['order_details']:
            for old_order_item in purge_new_details:
                if old_order_item.id == new_order_item['order_item_id']:
                    self.update_order_item(new_order_item, old_order_item)

        SyncOrders().sync_customer(my_order)

        return JsonResponse(
            {'message': 'actualizado con exito'}, status=201
        )

    def update_order_item(self, new_order_item, old_order_item):
        loggin_event(f'Actualizando item de orden {old_order_item.id}')
        current_data = {
            'order_item_id': old_order_item.pk,
            'id_stock_detail': old_order_item.id_stock_detail,
            'quantity': int(old_order_item.quantity),
            'box_model': old_order_item.box_model,
            'line_price': float(old_order_item.line_price),
            'total_stem_flower': int(old_order_item.tot_stem_flower)
        }
        new_data = {
            'order_item_id': new_order_item['order_item_id'],
            'id_stock_detail': new_order_item['id_stock_detail'],
            'quantity': new_order_item['quantity'],
            'box_model': new_order_item['box_model'],
            'line_price': float(new_order_item['line_price']),
            'total_stem_flower': new_order_item['tot_stem_flower'],
        }

        if current_data != new_data:
            old_order_item.id_stock_detail = new_order_item['id_stock_detail']
            old_order_item.quantity = new_order_item['quantity']
            old_order_item.box_model = new_order_item['box_model']
            old_order_item.line_total = new_order_item['line_total']
            old_order_item.is_modified = True
            old_order_item.save()
            # actualizamos las cajas de la orden
            self.update_box_items(old_order_item, new_order_item)

        return True

    def update_box_items(self, old_order_item, new_order_item):
        loggin_event(f'Actualizando cajas de la orden {old_order_item.id}')
        OrderBoxItems.disable_by_order_items(old_order_item)

        for new_box_item in new_order_item['box_items']:
            OrderBoxItems.objects.create(
                order_item=old_order_item,
                product=Product.get_by_id(new_box_item['product_id']),
                length=new_box_item['length'],
                qty_stem_flower=new_box_item['qty_stem_flower'],
                stem_cost_price=new_box_item['stem_cost_price'],
                profit_margin=new_box_item['margin']
            )

        return True
