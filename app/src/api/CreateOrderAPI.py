import json
from datetime import date
from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_datetime
from trade.models import Order, OrderItems, OrderBoxItems
from products.models import Product
from partners.models import Partner
from products.models import StockDetail, BoxItems
from partners.models import Partner


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

        order_total = self.getTotals(order_data['order'])
        order = Order.objects.create(
            partner=customer,
            type_document='ORD_VENTA',
            status='PENDIENTE',
            **order_total,
        )

        for new_order_item in order_data['order']:
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
                if not product:
                    return JsonResponse(
                        {'error': 'Product not found'},
                        status=404
                    )

                OrderBoxItems.objects.create(
                    order_item=order_item,
                    product=product,
                    length=box_item['length'],
                    qty_stem_flower=box_item['qty_stem_flower'],
                    stem_cost_price=box_item['stem_cost_price'],
                    profit_margin=float(box_item['margin'])
                )

            return JsonResponse(
                {'message': 'Order created successfully'},
                status=201
            )

    def getTotals(self, order):
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