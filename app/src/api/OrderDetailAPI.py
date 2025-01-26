from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from common import SerializerOrder


class OrderDetailAPI(APIView):
    def get(self, request, id_order, *args, **kwargs):
        order = Order.get_by_id(id_order)
        if not order:
            return JsonResponse({'error': 'El pedio no existe'}, status=404)

        order_details = OrderItems.get_by_order(order)
        result_dict = []
        for order_detail in order_details:
            result_dict.append(SerializerOrder.get_line(order_detail))

        return JsonResponse({
            'order': {
                'id': order.id,
                'date': order.date,
                'status': order.status,
                'type_document': order.type_document,
                'parent_order': order.parent_order,
                'total_price': order.total_price,
                'qb_total': order.qb_total,
                'hb_total': order.hb_total,
                'total_stem_flower': order.total_stem_flower,
                'partner': {
                    'id': order.partner.id,
                    'name': order.partner.name,
                    'address': order.partner.address,
                    'phone': order.partner.phone,
                    'email': order.partner.email,
                },
            },
            'order_details': result_dict
        },
            status=200
        )
