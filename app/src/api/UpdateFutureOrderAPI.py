from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from common import SyncOrders

from trade.models.Order import Order, OrderItems, OrderBoxItems
from partners.models import Partner
from products.models import Product
from common.AppLoger import loggin_event


class UpdateFutureOrderAPI(APIView):
    def __init__(self):
        super().__init__()

    @transaction.atomic
    def post(self, request):
        loggin_event('Recibiendo Datos por Post')
        # Obtener datos del request
        data = request.data

        order_id = data.get('order_id')
        order_data = data.get('order')
        customer_data = data.get('customer')
        supplier_data = data.get('supplier')
        order_lines = data.get('orderLines', [])

        # Validaciones básicas
        if not order_id:
            loggin_event('No se proporcionó el ID de la orden')
            return JsonResponse(
                {'error': 'No se proporcionó el ID de la orden'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not customer_data or not supplier_data:
            loggin_event('Cliente o proveedor no proporcionados')
            return JsonResponse(
                {'error': 'Cliente o proveedor no proporcionados'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener la orden a actualizar
        order = Order.get_by_id(order_id)
        if not order:
            loggin_event(f'Orden con ID {order_id} no encontrada')
            return JsonResponse(
                {'error': f'Orden con ID {order_id} no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que el cliente y proveedor existan
        customer = Partner.get_by_id(customer_data.get('id'))
        supplier = Partner.get_by_id(supplier_data.get('id'))

        if not supplier:
            supplier = Partner.get_partner_by_taxi_id('99999999999')

        if not customer or not supplier:
            loggin_event('Cliente o proveedor no encontrado')
            return JsonResponse(
                {'error': 'Cliente o proveedor no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Desactivar líneas y cajas existentes
        Order.disable_order_items(order)

        # Actualizar datos básicos de la orden
        order.partner = customer
        order.num_order = order_data.get('num_order', order.num_order)

        # Actualizar totales de la orden desde el payload
        order.total_price = Decimal(str(order_data.get('total_price', 0)))
        order.total_margin = Decimal(
            str(order_data.get('total_margin', 0)))
        order.qb_total = order_data.get('qb_total', 0)
        order.hb_total = order_data.get('hb_total', 0)
        order.fb_total = Decimal(str(order_data.get('fb_total', 0)))
        order.total_stem_flower = order_data.get('total_stem_flower', 0)

        # Si la orden estaba cancelada, cambiar su estado a MODIFICADO
        if order.status == 'CANCELADO':
            order.status = 'MODIFICADO'
        # Si no estaba facturada, mantenerla como PENDIENTE o MODIFICADO
        elif not order.is_invoiced:
            order.status = 'MODIFICADO' if order.status != 'PENDIENTE' else 'PENDIENTE'

        loggin_event(f'Orden actualizada {order.id}')
        order.save()

        # Procesar las líneas de la orden
        for line_data in order_lines:
            line = OrderItems()
            line.order = order
            line.box_model = line_data.get('box_model', 'QB')
            line.quantity = line_data.get('quantity', 1)

            # Calcular totales de la línea
            line_price = Decimal('0.00')
            line_margin = Decimal('0.00')
            tot_stem_flower = 0

            line.save()  # Guardar para obtener el ID

            # Procesar los items de caja
            for item_data in line_data.get('order_box_items', []):
                if not item_data.get('product'):
                    continue

                product_data = item_data.get('product')
                product = Product.objects.get(pk=product_data.get('id'))

                box_item = OrderBoxItems()
                box_item.order_item = line
                box_item.product = product
                box_item.length = item_data.get('length', 0)
                box_item.qty_stem_flower = item_data.get(
                    'qty_stem_flower', 0)
                box_item.stem_cost_price = Decimal(
                    str(item_data.get('stem_cost_price', 0)))
                box_item.profit_margin = Decimal(
                    str(item_data.get('profit_margin', 0)))
                box_item.total_bunches = item_data.get('total_bunches', 0)
                box_item.stems_bunch = item_data.get('stems_bunch', 0)

                box_item.save()

                # Actualizar totales de la línea
                item_price = box_item.stem_cost_price * \
                    Decimal(box_item.qty_stem_flower)
                item_margin = box_item.profit_margin * \
                    Decimal(box_item.qty_stem_flower)

                line_price += item_price
                line_margin += item_margin
                tot_stem_flower += box_item.qty_stem_flower

            # Actualizar totales de la línea
            line.line_price = line_price
            line.line_margin = line_margin
            line.line_total = line_price + line_margin
            line.tot_stem_flower = tot_stem_flower
            line.save()

        # Recalcular todos los totales
        Order.rebuild_totals(order)
        loggin_event(f'Totales recalculados para la orden {order.id}')

        loggin_event(
            f'Generando órdenes de compra asociadas para la orden {order.id}'
        )
        loggin_event('Verificamos tipo de orden de compra')
        if supplier.business_tax_id == '99999999999':
            loggin_event('Sincronizando pedidos de proveedor...')
            SyncOrders().sync_suppliers(order)

        return JsonResponse({
            'success': True,
            'message': 'Orden actualizada correctamente',
            'order_id': order.id
        }, status=status.HTTP_200_OK)
