from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from common import SerializerOrder
from partners.models import Contact


class OrderDetailAPI(View):
    def get(self, request, id_stock_day, *args, **kwargs):
        orders = Order.get_by_stock_day(id_stock_day)
        if len(orders) == 0:
            return JsonResponse({"data": []}, status=200)

        all_orders = []
        for order in orders:
            contact = Contact.get_principal_by_partner(order.partner)
            contact_dict = {}
            if contact:
                contact_dict = {
                    'name': contact.name,
                    'position': contact.position,
                    'contact_type': contact.contact_type,
                    'phone': contact.phone,
                    'email': contact.email,
                    'is_principal': contact.is_principal
                }
            item_order = {
                'order': {
                    'id': order.id,
                    'stock_day': order.stock_day.id,
                    'date': order.date.isoformat(),
                    'status': order.status,
                    'type_document': order.type_document,
                    'parent_order': order.parent_order,
                    'total_price': float(order.total_price),
                    'qb_total': order.qb_total,
                    'hb_total': order.hb_total,
                    'total_stem_flower': order.total_stem_flower,
                    'partner': {
                        'id': order.partner.id,
                        'name': order.partner.name,
                        'address': order.partner.address,
                        'phone': order.partner.phone,
                        'email': order.partner.email,
                        'contact': contact_dict
                    },
                },
                'is_selected': False,
                'order_details': []
            }

            order_details = OrderItems.get_by_order(order.id)
            for order_detail in order_details:
                item_order['order_details'].append(
                    SerializerOrder().get_line(order_detail)
                )

            all_orders.append(item_order)

        return JsonResponse(
            all_orders,
            status=200,
            safe=False
        )
