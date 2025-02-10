from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from common import SerializerSupplierOrder
from partners.models import Contact


class OrderPurchaseByOrderSale(View):
    def get(self, request, order_customer_id):
        order_customer = Order.get_order_by_id(order_customer_id)
        if not order_customer:
            return JsonResponse(
                {'error': 'No existe la orden de venta'},
                status=404
            )

        if order_customer.type_document != 'ORD_VENTA':
            return JsonResponse({
                'error': 'El documento no es una orden de venta'
            }, status=404)

        orders_supplier = Order.get_by_sale_order(order_customer)
        if not orders_supplier:
            return JsonResponse(
                {},
                status=200
            )

        supplier_orders = Order.get_by_sale_order(order_customer)

        all_orders = []
        for order in supplier_orders:
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
                        'skype': order.partner.skype,
                        'business_tax_id': order.partner.business_tax_id,
                        'contact': contact_dict
                    },
                },
                'order_details': [],
                'is_selected': False,
                'is_cancelled': False,
                'is_modified': False,
                'is_confirmed': False,
            }

            order_details = OrderItems.get_by_order(order.id)
            for order_detail in order_details:
                item_order['order_details'].append(
                    SerializerSupplierOrder().get_line(order_detail)
                )

            all_orders.append(item_order)

        return JsonResponse(
            all_orders,
            status=200,
            safe=False
        )
