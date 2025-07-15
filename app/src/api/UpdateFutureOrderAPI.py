import json
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from common import SyncOrders

from trade.models.Order import Order, OrderItems, OrderBoxItems
from partners.models import Partner
from products.models import Product
from common.AppLoger import loggin_event


class UpdateFutureOrderAPI(View):
    def __init__(self):
        super().__init__()

    def parse_date(self, date_str):
        """Convierte diferentes formatos de fecha a YYYY-MM-DD o None si está vacío"""
        if not date_str or date_str.strip() == '':
            return None

        try:
            # Si viene en formato DD/MM/YYYY HH:MM
            if '/' in date_str:
                # Tomar solo la parte de fecha
                date_part = date_str.split(' ')[0]
                day, month, year = date_part.split('/')
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            # Si ya viene en formato YYYY-MM-DD
            elif '-' in date_str and len(date_str.split('-')[0]) == 4:
                return date_str.split(' ')[0]  # Tomar solo la parte de fecha
            else:
                return None
        except:
            return None

    @transaction.atomic
    def post(self, request):
        loggin_event('Recibiendo Datos por Post')
        # Obtener datos del request
        data = json.loads(request.body)

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
        order.supplier = supplier
        order.num_order = order_data.get('num_order', order.num_order)

        # Manejar delivery_date con validación
        delivery_date = self.parse_date(order_data.get('delivery_date', ''))
        if delivery_date:
            order.delivery_date = delivery_date
        # Si delivery_date es None o vacío, mantener el valor actual o asignar None
        elif not order.delivery_date:
            order.delivery_date = None

        order.discount = Decimal(str(order_data.get('discount', 0)))

        # Actualizar totales de la orden desde el payload
        order.total_price = Decimal(str(order_data.get('total_price', 0)))
        order.total_margin = Decimal(str(order_data.get('total_margin', 0)))
        order.qb_total = order_data.get('qb_total', 0)
        order.hb_total = order_data.get('hb_total', 0)
        order.fb_total = Decimal(str(order_data.get('fb_total', 0)))
        order.total_stem_flower = order_data.get('total_stem_flower', 0)
        order.total_bunches = order_data.get('total_bunches', 0)

        # Actualizar el estado según el payload
        if order_data.get('status'):
            order.status = order_data.get('status')
        elif order.status == 'CANCELADO':
            order.status = 'MODIFICADO'
        elif not order.is_invoiced:
            order.status = 'MODIFICADO' if order.status != 'PENDIENTE' else 'PENDIENTE'

        loggin_event(
            f'Orden actualizada {order.id} - Cliente: {customer.name} - Proveedor: {supplier.name}')
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

        # NUEVA FUNCIONALIDAD: Actualizar órdenes de compra relacionadas
        self.update_related_purchase_orders(order, supplier)

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

    def update_related_purchase_orders(self, sale_order, supplier):
        """Actualizar las órdenes de compra relacionadas con la orden de venta"""
        loggin_event(
            f'Actualizando órdenes de compra relacionadas con la orden {sale_order.id}')

        # Buscar órdenes de compra relacionadas
        purchase_orders = Order.objects.filter(
            parent_order=sale_order,
            type_document='ORD_COMPRA',
            is_active=True
        )

        if not purchase_orders.exists():
            loggin_event(
                f'No se encontraron órdenes de compra para actualizar')
            return

        # Obtener todos los items de la orden de venta agrupados por proveedor
        sale_order_items = OrderItems.get_by_order(sale_order)

        for purchase_order in purchase_orders:
            loggin_event(f'Actualizando orden de compra {purchase_order.id}')

            # Desactivar items existentes de la orden de compra
            Order.disable_order_items(purchase_order)

            # Recrear items basados en la orden de venta
            self.recreate_purchase_order_items(
                purchase_order, sale_order_items, supplier)

            # Recalcular totales de la orden de compra
            Order.rebuild_totals(purchase_order)

            loggin_event(
                f'Orden de compra {purchase_order.id} actualizada correctamente')

    def recreate_purchase_order_items(self, purchase_order, sale_order_items, supplier):
        """Recrear los items de la orden de compra basados en la orden de venta"""

        for sale_line in sale_order_items:
            # Crear nueva línea en la orden de compra
            purchase_line = OrderItems()
            purchase_line.order = purchase_order
            purchase_line.box_model = sale_line.box_model
            purchase_line.quantity = sale_line.quantity
            purchase_line.tot_stem_flower = sale_line.tot_stem_flower
            purchase_line.total_bunches = sale_line.total_bunches
            purchase_line.line_price = sale_line.line_price
            purchase_line.line_margin = sale_line.line_margin
            purchase_line.line_commission = sale_line.line_commission
            purchase_line.line_total = (sale_line.line_price +
                                        sale_line.line_margin)
            purchase_line.save()

            # Obtener los box items de la línea de venta
            sale_box_items = OrderBoxItems.get_box_items(sale_line)

            for sale_box_item in sale_box_items:
                # Crear box item en la orden de compra (copiando profit_margin)
                purchase_box_item = OrderBoxItems()
                purchase_box_item.order_item = purchase_line
                purchase_box_item.product = sale_box_item.product
                purchase_box_item.length = sale_box_item.length
                purchase_box_item.qty_stem_flower = (
                    sale_box_item.qty_stem_flower)
                purchase_box_item.stem_cost_price = (
                    sale_box_item.stem_cost_price)
                purchase_box_item.profit_margin = sale_box_item.profit_margin
                purchase_box_item.total_bunches = sale_box_item.total_bunches
                purchase_box_item.stems_bunch = sale_box_item.stems_bunch
                purchase_box_item.save()

                loggin_event(
                    f'Box item creado: {sale_box_item.product.name} - '
                    f'Cantidad: {sale_box_item.qty_stem_flower}'
                )
