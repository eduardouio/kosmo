import json
from django.views import View
from django.http import JsonResponse
from trade.models.Order import Order, OrderItems, OrderBoxItems
from products.models import Product
from partners.models import Partner
from datetime import datetime


class CreateFutureOrderAPI(View):

    def post(self, request):
        data = json.loads(request.body)

        # Extraer las secciones principales de datos
        order_data = data.get('order', {})
        order_lines = data.get('orderLines', [])
        customer_data = data.get('customer', {})
        supplier_data = data.get('supplier', {})

        # Crear el objeto de orden
        order = Order()
        order.serie = order_data.get('serie', '200')
        order.consecutive = 0  # Ignorar número consecutivo como solicitado

        # Parsear fecha si está proporcionada
        date_str = order_data.get('date')
        if date_str:
            try:
                # Formato de fecha "DD/MM/YYYY HH:MM"
                order.date = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
            except ValueError:
                pass

        # Establecer socio basado en type_document
        order.type_document = order_data.get('type_document')

        if order.type_document == 'ORD_COMPRA':
            partner_id = supplier_data.get('id')
            order.partner = Partner.objects.get(id=partner_id)
        else:  # ORD_VENTA
            partner_id = customer_data.get('id')
            order.partner = Partner.objects.get(id=partner_id)

        # Establecer otros campos de la orden
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

        # Guardar la orden para obtener un ID
        order.save()

        # Crear items de la orden
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

            # Guardar el item de orden para obtener un ID
            order_item.save()

            # Crear items de caja
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

                # Guardar el item de caja
                box_item.save()

        # Recalcular totales para asegurar consistencia
        Order.rebuild_totals(order)

        return JsonResponse({
            'message': 'Future order created successfully', 'order_id': order.id
        }, status=201
        )
