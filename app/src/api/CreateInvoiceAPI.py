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
