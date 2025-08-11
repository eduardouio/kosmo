import json
from django.http import JsonResponse
from django.views import View
from common.SyncOrders import SyncOrders
from common.AppLoger import loggin_event
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import Product


class UpdateCustmerOrderAPI(View):
    def post(self, request):
        loggin_event('Actualizando orden de cliente')
        order_data = json.loads(request.body)
        my_order = Order.objects.get(id=order_data['order']['id'])

        if my_order.type_document != 'ORD_VENTA':
            return JsonResponse(
                {'error': 'No se puede modificar una orden de compra'},
                status=400
            )

        Order.disable_order_items(my_order)

        # actualizo los items de la orden
        for new_order_item in order_data['order_details']:
            new_ord_item = OrderItems.objects.create(
                order=my_order,
                id_stock_detail=new_order_item['id_stock_detail'],
                line_price=float(new_order_item['line_price']),
                line_margin=float(new_order_item['line_margin']),
                line_total=float(new_order_item['line_total']),
                box_model=new_order_item['box_model'],
                quantity=new_order_item['quantity'],
                tot_stem_flower=new_order_item['tot_stem_flower'],
            )

            for new_box_item in new_order_item['box_items']:
                OrderBoxItems.objects.create(
                    order_item=new_ord_item,
                    product=Product.get_by_id(new_box_item['product_id']),
                    length=new_box_item['length'],
                    qty_stem_flower=new_box_item['qty_stem_flower'],
                    stem_cost_price=new_box_item['stem_cost_price'],
                    profit_margin=new_box_item['margin']
                )

    # Recalcular totales de la orden (líneas y cabeceras)
    # Garantiza que cambios de costo/margen se reflejen correctamente
        Order.rebuild_totals(my_order)

    # Sincronizar órdenes de proveedores con totales correctos
        SyncOrders().sync_suppliers(my_order)

        return JsonResponse(
            {'message': 'actualizado con exito'}, status=201
        )
