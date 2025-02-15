import json
from django.http import JsonResponse
from django.views import View
from common import SerializerCustomerOrder, SyncOrdersSupplier
from partners.models import Contact, Partner
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import Product


class UpdateCustmerOrderAPI(View):
    def post(self, request):
        order_data = json.loads(request.body)
        my_order = Order.objects.get(id=order_data['order']['id'])

        if my_order.type_document != 'ORD_VENTA':
            return JsonResponse(
                {'error': 'No se puede modificar una orden de compra'},
                status=400
            )

        order_items = OrderItems.get_by_order(my_order)
        [OrderItems.disable_order_item(order_item)
            for order_item in order_items
         ]

        for order_item in order_data['order_details']:
            new_order_item = OrderItems.objects.create(
                order=my_order,
                id_stock_detail=order_item['id_stock_detail'],
                box_model=order_item['box_model'],
                quantity=order_item['quantity'],
            )

            for box_item in order_item['box_items']:
                OrderBoxItems.objects.create(
                    order_item=new_order_item,
                    product=Product.get_by_id(box_item['product_id']),
                    qty_stem_flower=box_item['qty_stem_flower'],
                    stem_cost_price=box_item['stem_cost_price'],
                    profit_margin=box_item['margin'],
                    length=box_item['length'],
                )

            OrderItems.rebuild_order_item(new_order_item)

        Order.rebuild_totals(my_order)

        # armamos la respuesta
        contact = Contact.get_principal_by_partner(my_order.partner)
        contact_dict = {}
        if contact:
            contact_dict = {
                'name': contact.name,
                'position': contact.position,
                'contact_type': contact.contact_type,
                'phone': contact.phone,
            }
        order_items = OrderItems.get_by_order(my_order)
        order_details = [
            SerializerCustomerOrder().get_line(i)
            for i in order_items
        ]

        result = {
            'order': {
                'id': my_order.id,
                'stock_day': my_order.stock_day.id,
                'date': my_order.date.isoformat(),
                'status': my_order.status,
                'type_document': my_order.type_document,
                'parent_my_order': my_order.parent_order,
                'total_price': float(my_order.total_price),
                'qb_total': my_order.qb_total,
                'hb_total': my_order.hb_total,
                'total_stem_flower': my_order.total_stem_flower,
                'partner': {
                    'id': my_order.partner.id,
                    'name': my_order.partner.name,
                    'address': my_order.partner.address,
                    'phone': my_order.partner.phone,
                    'email': my_order.partner.email,
                    'skype': my_order.partner.skype,
                    'business_tax_id': my_order.partner.business_tax_id,
                    'contact': contact_dict
                },
            },
            'order_details': order_details,
            'is_selected': False,
            'is_cancelled': False,
            'is_modified': False,
            'is_confirmed': False,
        }
        SyncOrdersSupplier().update_supplier_orders(my_order)
        return JsonResponse(
            result, status=201,
            safe=False
        )
