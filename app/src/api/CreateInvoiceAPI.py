import json
from trade.models import Order
from common.AppLoger import loggin_event
from common import CreateInvoiceByOrder
from django.views import View
from django.http import JsonResponse


class CreateInvoiceAPI(View):

    def get(self, request, *args, **kwargs):
        loggin_event(f'CreateInvoiceAPI GET Create Invoice {request.user}')
        return JsonResponse({'message': 'GET method not allowed'}, status=405)

    def post(self, request, *args, **kwargs):
        loggin_event(f'CreateInvoiceAPI POST Create Invoice {request.user}')
        request_data = json.loads(request.body)
        order_id = request_data.get('order_id')
        order = Order.get_order_by_id(order_id)

        if order is None:
            loggin_event(f"El pedido {order_id} no existe")
            return JsonResponse({'error': 'La Orden No Existe'}, status=404)

        if order.status == 'FACTURADO':
            loggin_event(f"El pedido {order_id} ya tiene una factura")
            return JsonResponse({'error': 'Pedido Facturado'}, status=400)

        if order.status == 'CANCELADO':
            loggin_event(f"El pedido {order_id} esta cancelado")
            return JsonResponse({'error': 'Pedido Cancelado'}, status=400)

        if order.status == 'PENDIENTE':
            loggin_event(f"El pedido {order_id} esta pendiente")
            return JsonResponse({'error': 'Pedido Pendiente'}, status=400)

        invoice = CreateInvoiceByOrder().generate_invoice(order)

        # Si es una orden de venta, crear facturas de compra automáticamente
        if order.type_document == 'ORD_VENTA':
            self.create_purchase_invoices(order)

        response_data = {
            'invoice_id': invoice.id,
            'order_id': order.id,
            'num_invoice': invoice.num_invoice,
            'num_order': order.num_order,
            'customer_name': invoice.partner.name,
            'customer_id': invoice.partner.id,
            'total_price': invoice.total_price,
            'total_margin': invoice.total_margin
        }

        return JsonResponse(response_data, status=201)

    def create_purchase_invoices(self, sale_order):
        """Crear facturas de compra para todas las órdenes de compra relacionadas"""
        from trade.models import Invoice, InvoiceItems, InvoiceBoxItems, OrderItems, OrderBoxItems
        from datetime import datetime, timedelta

        loggin_event(
            f'Creando facturas de compra para orden de venta {sale_order.id}')

        # Obtener órdenes de compra relacionadas
        purchase_orders = Order.get_by_parent_order(sale_order)

        if not purchase_orders:
            loggin_event('No hay órdenes de compra para facturar')
            return

        for purchase_order in purchase_orders:
            if purchase_order.is_invoiced:
                loggin_event(
                    f'Orden de compra {purchase_order.id} ya está facturada')
                continue

            loggin_event(
                f'Creando factura para orden de compra {purchase_order.id}')

            # Calcular fecha de vencimiento
            days = purchase_order.partner.credit_term if purchase_order.partner.credit_term else 30
            due_date = datetime.now() + timedelta(days=days)

            # Crear número de factura con formato SinFact-{serie-consecutivo}
            num_invoice = f"SinFact-{purchase_order.serie or '200'}-{str(purchase_order.consecutive or 0).zfill(6)}"
            loggin_event(f'Número de factura: {purchase_order.__str__()}')
            # Crear factura de compra
            purchase_invoice = Invoice.objects.create(
                order=purchase_order,
                partner=purchase_order.partner,
                type_document='FAC_COMPRA',
                date=datetime.now(),
                due_date=due_date,
                status='PENDIENTE',
                num_invoice=num_invoice,
                serie='',  # Serie en blanco como solicitado
                consecutive=None,  # Consecutivo en blanco como solicitado
                total_price=purchase_order.total_price,
                total_margin=sale_order.total_margin,  # Sin margen en factura de compra
                qb_total=purchase_order.qb_total,
                hb_total=purchase_order.hb_total,
                fb_total=purchase_order.fb_total,
                tot_stem_flower=purchase_order.total_stem_flower,
                total_bunches=purchase_order.total_bunches
            )

            # Copiar items de la orden a la factura
            self.copy_order_items_to_invoice(purchase_order, purchase_invoice)

            # Actualizar orden de compra
            purchase_order.status = 'FACTURADO' 
            purchase_order.is_invoiced = True
            purchase_order.id_invoice = purchase_invoice.id
            purchase_order.num_invoice = purchase_invoice.num_invoice
            purchase_order.save()

            loggin_event(
                f'Factura de compra creada: {purchase_invoice.num_invoice}')

    def copy_order_items_to_invoice(self, order, invoice):
        """Copiar items de la orden a la factura"""
        from trade.models import InvoiceItems, InvoiceBoxItems, OrderItems, OrderBoxItems

        order_items = OrderItems.get_by_order(order)
        for order_item in order_items:
            # Crear item de factura
            invoice_item = InvoiceItems.objects.create(
                invoice=invoice,
                id_order_item=order_item.id,
                box_model=order_item.box_model,
                quantity=order_item.quantity,
                tot_stem_flower=order_item.tot_stem_flower,
                line_price=order_item.line_price,
                line_margin=0,  # Sin margen en factura de compra
                line_total=order_item.line_price,
                total_bunches=order_item.total_bunches  # Agregar total_bunches
            )

            # Copiar box items
            box_items = OrderBoxItems.get_box_items(order_item)
            for box_item in box_items:
                InvoiceBoxItems.objects.create(
                    invoice_item=invoice_item,
                    product=box_item.product,
                    length=box_item.length,
                    qty_stem_flower=box_item.qty_stem_flower,
                    stem_cost_price=box_item.stem_cost_price,
                    profit_margin=0,  # Sin margen en factura de compra
                    total_bunches=box_item.total_bunches,  # Agregar total_bunches
                    stems_bunch=box_item.stems_bunch  # Agregar stems_bunch
                )
