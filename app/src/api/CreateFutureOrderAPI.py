import json
from django.views import View
from django.http import JsonResponse
from trade.models.Order import Order, OrderItems, OrderBoxItems
from products.models import Product
from partners.models import Partner
from datetime import datetime
from common.AppLoger import loggin_event


class CreateFutureOrderAPI(View):

    def post(self, request):
        data = json.loads(request.body)
        loggin_event('Recibiendo solicitud de creacion de orden Futura')
        loggin_event(f'Datos recibidos: {data}')

        order_data = data.get('order', {})
        order_lines = data.get('orderLines', [])
        customer_data = data.get('customer', {})
        supplier_data = data.get('supplier', {})

        # Crear orden de cliente (customer)
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
        order.total_bunches = order_data.get('total_bunches', 0)
        order.save()
        loggin_event(f'Orden futura creada con éxito {order.id}')

        # Crear líneas de la orden de cliente
        created_orders_items = []
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

            # Calcular total de ramos para este ítem
            total_bunches_item = 0
            for box_item_data in line_data.get('order_box_items', []):
                total_bunches_item += box_item_data.get('total_bunches', 0)

            order_item.total_bunches = total_bunches_item
            order_item.save()
            created_orders_items.append(order_item)

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

        # Crear orden de compra para el proveedor directamente
        if supplier_data.get('id'):
            # Obtener el proveedor por ID
            supplier = Partner.get_by_id(supplier_data.get('id'))

            if supplier:
                # Crear la orden de compra
                purchase_order = Order()
                purchase_order.serie = '200'
                purchase_order.consecutive = Order.get_next_purchase_consecutive()
                purchase_order.date = datetime.now()
                purchase_order.type_document = 'ORD_COMPRA'
                purchase_order.total_margin = order_data.get('total_margin', 0)
                purchase_order.partner = supplier
                purchase_order.num_order = order.num_order
                purchase_order.status = 'PENDIENTE'
                purchase_order.parent_order = order  # Referencia a la orden del cliente
                purchase_order.save()

                loggin_event(
                    f'Orden de compra creada con éxito {purchase_order.id} para proveedor {supplier.name}')

                # Copiar los ítems de la orden del cliente a la orden de compra
                for customer_order_item in created_orders_items:
                    # Crear item de orden de compra
                    purchase_order_item = OrderItems()
                    purchase_order_item.order = purchase_order
                    purchase_order_item.id_stock_detail = customer_order_item.id_stock_detail
                    purchase_order_item.box_model = customer_order_item.box_model
                    purchase_order_item.quantity = customer_order_item.quantity
                    purchase_order_item.tot_stem_flower = customer_order_item.tot_stem_flower
                    purchase_order_item.total_bunches = customer_order_item.total_bunches
                    purchase_order_item.line_price = customer_order_item.line_price
                    purchase_order_item.line_margin = customer_order_item.line_margin
                    purchase_order_item.line_commission = customer_order_item.line_commission
                    purchase_order_item.line_total = customer_order_item.line_price + customer_order_item.line_margin
                    purchase_order_item.save()

                    # Copiar los ítems de cajas
                    customer_box_items = OrderBoxItems.get_by_order_item(
                        customer_order_item
                    )
                    for customer_box_item in customer_box_items:
                        purchase_box_item = OrderBoxItems()
                        purchase_box_item.order_item = purchase_order_item
                        purchase_box_item.product = customer_box_item.product
                        purchase_box_item.length = customer_box_item.length
                        purchase_box_item.qty_stem_flower = customer_box_item.qty_stem_flower
                        purchase_box_item.stem_cost_price = customer_box_item.stem_cost_price
                        purchase_box_item.total_bunches = customer_box_item.total_bunches
                        purchase_box_item.stems_bunch = customer_box_item.stems_bunch
                        purchase_box_item.profit_margin = customer_box_item.profit_margin
                        purchase_box_item.save()

                        loggin_event(
                            f'Item de caja de orden de compra guardado con éxito {purchase_box_item.id}')

                # Actualizar totales de la orden de compra
                Order.rebuild_totals(purchase_order)
                loggin_event(f'Totales de orden de compra recalculados')
            else:
                loggin_event(
                    f'No se pudo encontrar el proveedor con ID {supplier_data.get("id")}', error=True)

        return JsonResponse({
            'message': 'Orden Futura Creada', 'order_id': order.id
        }, status=201
        )
