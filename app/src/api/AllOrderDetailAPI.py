from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from common import SerializerCustomerOrder
from partners.models import Contact
from common.AppLoger import loggin_event


class AllOrderDetailAPI(View):
    def get(self, request, id_stock_day, *args, **kwargs):
        if request.GET.get('type') == 'purchase':
            loggin_event(
                'Obteniendo todas las compras de stock #{}'.format(
                    id_stock_day
                )
            )
            orders = Order.get_sales_by_stock_day(id_stock_day)
        else:
            loggin_event(
                'Obteniendo todas las ventas de stock #{}'.format(id_stock_day)
            )
            orders = Order.get_purchases_by_stock_day(id_stock_day)

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
            parent_order = {}
            if order.parent_order:
                parent_order = {
                    'id': order.parent_order.id,
                    'id_customer': order.parent_order.partner.id,
                    'customer': order.parent_order.partner.name,
                    'total_price': float(order.parent_order.total_price),
                    'qb_total': order.parent_order.qb_total,
                    'hb_total': order.parent_order.hb_total,
                    'total_stem_flower': order.parent_order.total_stem_flower,
                    'status': order.parent_order.status,
                    'num_invoice': order.parent_order.num_invoice,
                }
            item_order = {
                'order': {
                    'id': order.id,
                    'stock_day': order.stock_day.id,
                    'date': order.date.isoformat(),
                    'status': order.status,
                    'serie': order.serie,
                    'consecutive': order.consecutive,
                    'type_document': order.type_document,
                    'parent_order': parent_order,
                    'total_price': float(order.total_price),
                    'qb_total': order.qb_total,
                    'hb_total': order.hb_total,
                    'total_stem_flower': order.total_stem_flower,
                    'total_bunches': order.total_bunches,
                    'num_invoice': order.num_invoice,
                    'is_invoiced': order.is_invoiced,
                    'id_invoice': order.id_invoice,
                    'partner': {
                        'id': order.partner.id,
                        'name': order.partner.name,
                        'address': order.partner.address,
                        'phone': order.partner.phone,
                        'email': order.partner.email,
                        'skype': order.partner.skype,
                        'business_tax_id': order.partner.business_tax_id,
                        'contact': contact_dict
                    },
                },
                'order_details': [],
                'is_selected': False,
                'is_modified': False,
                'is_cancelled': order.status == 'CANCELADO',
                'is_confirmed': order.status == 'CONFIRMADO' or order.is_invoiced,
                'is_invoiced': order.is_invoiced,
                'id_invoice': order.id_invoice,
            }

            order_details = OrderItems.get_by_order(order.id)
            for order_detail in order_details:
                item_order['order_details'].append(
                    SerializerCustomerOrder().get_line(order_detail)
                )

            all_orders.append(item_order)

        loggin_event('Ordenes obtenidas de stock #{}'.format(id_stock_day))

        return JsonResponse(
            all_orders,
            status=200,
            safe=False
        )
