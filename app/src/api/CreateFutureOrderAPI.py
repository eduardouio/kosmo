import json
from django.views import View
from django.http import JsonResponse
from trade.models.Order import Order, OrderItems, OrderBoxItems
from products.models import Product
from partners.models import Partner
from datetime import datetime
from common.AppLoger import loggin_event
from common import SyncOrders


class CreateFutureOrderAPI(View):

    def post(self, request):
        data = json.loads(request.body)
        loggin_event('Recibiendo solicitud de creaciond e orden Futura')

        order_data = data.get('order', {})
        order_lines = data.get('orderLines', [])
        customer_data = data.get('customer', {})
        supplier_data = data.get('supplier', {})

        order = Order()
        order.serie = order_data.get('serie', '200')
        order.consecutive = Order.get_next_sale_consecutive()
        order.date = datetime.now()
        order.type_document = order_data.get('type_document')
        order.partner = Partner.get_by_id(customer_data.get('id'))
        order.num_order = order_data.get('num_order')
        delivery_date_str = order_data.get('delivery_date')
        if delivery_date_str:
            try:
                order.delivery_date = datetime.strptime(
                    delivery_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass

        order.status = order_data.get('status', 'PENDIENTE')
        order.discount = order_data.get('discount', 0)
        order.total_price = order_data.get('total_price', 0)
        order.total_margin = order_data.get('total_margin', 0)
        order.comision_seler = order_data.get('comision_seler', 0)
        order.qb_total = order_data.get('qb_total', 0)
        order.hb_total = order_data.get('hb_total', 0)
        order.fb_total = order_data.get('fb_total', 0)
        order.total_stem_flower = order_data.get('total_stem_flower', 0)
        order.save()
        loggin_event(f'Orden futura creada con éxito {order.id}')

        for line_data in order_lines:
            order_item = OrderItems()
            order_item.order = order
            order_item.id_stock_detail = line_data.get('id_stock_detail', 0)
            order_item.line_price = line_data.get('line_price', 0)
            order_item.line_margin = line_data.get('line_margin', 0)
            order_item.line_total = line_data.get('line_total', 0)
            order_item.line_commission = line_data.get('line_commission', 0)
            order_item.tot_stem_flower = line_data.get('tot_stem_flower', 0)
            order_item.box_model = line_data.get('box_model', 'QB')
            order_item.quantity = line_data.get('quantity', 1)
            order_item.save()

            for box_item_data in line_data.get('order_box_items', []):
                product_data = box_item_data.get('product', {})
                product_id = product_data.get('id')

                box_item = OrderBoxItems()
                box_item.order_item = order_item
                box_item.product = Product.objects.get(id=product_id)
                box_item.length = box_item_data.get('length', 0)
                box_item.stems_bunch = box_item_data.get('stems_bunch', 0)
                box_item.total_bunches = box_item_data.get('total_bunches', 0)
                box_item.qty_stem_flower = box_item_data.get(
                    'qty_stem_flower', 0)
                box_item.stem_cost_price = float(
                    box_item_data.get('stem_cost_price', 0))
                box_item.profit_margin = float(
                    box_item_data.get('profit_margin', 0))

                box_item.save()
                loggin_event(f'Item de caja guardado con éxito {box_item.id}')

        Order.rebuild_totals(order)

        if supplier_data.get('business_tax_id', '9999999999') != '9999999999':
            self.create_purchase_order(
                customer_order=order, is_partner=supplier_data.get('id')
            )

        return JsonResponse({
            'message': 'Orden Futura Creada', 'order_id': order.id
        }, status=201
        )

    def create_purchase_order(self, customer_order, is_partner):
        loggin_event(
            f'Creando Orden de Compra parapedido {customer_order.id} '
            f'con proveedor {is_partner}'
        )
        purchase_order = Order()
        purchase_order.serie = '200'
        purchase_order.consecutive = Order.get_next_purchase_consecutive()
        purchase_order.date = datetime.now()
        purchase_order.type_document = 'ORD_COMPRA'
        purchase_order.partner = customer_order.partner
        purchase_order.num_order = customer_order.num_order
        purchase_order.status = 'PENDIENTE'
        purchase_order.save()

