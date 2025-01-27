import json
from decimal import Decimal
from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems, OrderBoxItems
from products.models import Product
from partners.models import Partner
from common import SerializerOrder


class CreateOrderAPI(View):
    def post(self, request):
        order_data = json.loads(request.body)
        if not order_data:
            return JsonResponse({'error': 'No data provided'}, status=400)

        customer = Partner.get_partner_by_id(order_data['customer']['id'])
        if not customer:
            return JsonResponse(
                {'error': 'Customer not found'},
                status=404
            )

        order_total = self.getOrderTotals(order_data['order_detail'])
        order = Order.objects.create(
            partner=customer,
            type_document='ORD_VENTA',
            status='PENDIENTE',
            **order_total,
        )

        for new_order_item in order_data['order_detail']:
            item_totals = self.getItemTotal(new_order_item)
            order_item = OrderItems.objects.create(
                order=order,
                id_stock_detail=new_order_item['stock_detail_id'],
                box_model=new_order_item['box_model'],
                quantity=new_order_item['quantity'],
                **item_totals
            )

            for box_item in new_order_item['box_items']:
                product = Product.get_by_id(box_item['product_id'])

                OrderBoxItems.objects.create(
                    order_item=order_item,
                    product=product,
                    length=box_item['length'],
                    qty_stem_flower=box_item['qty_stem_flower'],
                    stem_cost_price=box_item['stem_cost_price'],
                    profit_margin=float(box_item['margin'])
                )

        order_items = OrderItems.get_by_order(order)
        order_items_list = []
        for item in order_items:
            order_items_list.append(SerializerOrder().get_line(item))

        result = {
            'order': {
                'id': order.id,
                'status': order.status,
                'type_document': order.type_document,
                'qb_total': order.qb_total,
                'hb_total': order.hb_total,
                'discount': order.discount,
                'total_stem_flower': order.total_stem_flower,
                'total_price': order.total_price,
            },
            'order_detail': order_items_list,
        }

        return JsonResponse(
            {
                'message': 'Pedido Creado Exitosamente',
                'data': json.dumps(result, default=self.custom_serializer),
            },
            status=201
        )

    def getOrderTotals(self, order):
        totals = {
            ''
            'qb_total': 0,
            'hb_total': 0,
            'discount': 0,
            'total_stem_flower': 0,
            'total_price': 0,
        }

        for item in order:
            totals['qb_total'] += item['quantity'] if item['box_model'] == 'QB' else 0
            totals['hb_total'] += item['quantity'] if item['box_model'] == 'HB' else 0

            for box in item['box_items']:
                totals['total_stem_flower'] += box['qty_stem_flower']
                totals['total_price'] += (
                    box['qty_stem_flower']
                    * (float(box['margin']) + box['stem_cost_price'])
                )

        return totals

    def getItemTotal(self, order_item):
        totals = {
            'line_price': 0,
            'line_margin': 0,
            'line_total': 0,
            'tot_stem_flower': 0,
        }

        for item in order_item['box_items']:
            totals['tot_stem_flower'] += item['qty_stem_flower']
            totals['line_price'] += (
                item['stem_cost_price'] * item['qty_stem_flower']
            )
            totals['line_margin'] += (
                float(item['margin']) * item['qty_stem_flower']
            )
            totals['line_total'] += (
                (float(item['margin']) + item['stem_cost_price'])
                * item['qty_stem_flower']
            )

        return totals

    def custom_serializer(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Tipo no serializable: {type(obj)}")
