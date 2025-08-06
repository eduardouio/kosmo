from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from common.SerializerCustomerOrder import SerializerCustomerOrder
from common.SerializerSupplierOrder import SerializerSupplierOrder
from partners.models import Contact
from common.AppLoger import loggin_event


class OrderDetailAPI(View):
    def get(self, request, order_id, *args, **kwargs):
        order = Order.get_order_by_id(order_id)

        if not order:
            return JsonResponse({"error": "Orden no encontrada"}, status=404)

        loggin_event(f'Obteniendo detalles de la orden #{order_id}')

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

        order_data = {
            'order': {
                'id': order.id,
                'stock_day': order.stock_day.id if order.stock_day else None,
                'date': order.date.isoformat(),
                'status': order.status,
                'type_document': order.type_document,
                'parent_order': parent_order,
                'total_price': float(order.total_price),
                'qb_total': order.qb_total,
                'hb_total': order.hb_total,
                'total_stem_flower': order.total_stem_flower,
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
        serializer = SerializerCustomerOrder(
        ) if order.type_document == 'ORD_VENTA' else SerializerSupplierOrder()

        for order_detail in order_details:
            order_data['order_details'].append(
                serializer.get_line(order_detail)
            )

        loggin_event(f'Detalles de orden {order_id} obtenidos exitosamente')

        return JsonResponse(
            order_data,
            status=200,
            safe=False
        )
