from django.http import JsonResponse
from django.views import View
from django.utils.dateparse import parse_datetime
from trade.models import Order, OrderItems, OrderBoxItems
from products.models import StockDetail, BoxItems
from partners.models import Partner
import json


class CreateOrderAPI(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            if not data:
                return JsonResponse({'error': 'No data provided'}, status=400)
            
            import ipdb; ipdb.set_trace()

            for order_data in data:
                partner_data = order_data.get('partner', {}).get('_custom', {}).get('value', {})
                partner = Partner.objects.get(id=partner_data['id'])

                order = Order.objects.create(
                    partner=partner,
                    type_document='ORD_VENTA',
                    status='PENDIENTE',
                    qb_total=0,
                    hb_total=0,
                    total_price=0,
                )

                for item_data in order_data['box_items']:
                    item = item_data['_custom']['value']
                    stock_detail = StockDetail.objects.get(id=item['stock_detail_id'])

                    order_item = OrderItems.objects.create(
                        order=order,
                        stock_detail=stock_detail,
                        line_price=item['stem_cost_price'],
                        qty_stem_flower=item['qty_stem_flower'],
                        box_model=order_data['box_model'],
                        tot_stem_flower=order_data['tot_stem_flower'],
                        tot_cost_price_box=order_data['tot_cost_price_box'],
                        profit_margin=item['margin'],
                    )

                    OrderBoxItems.objects.create(
                        order_item=order_item,
                        product_id=item['product_id'],
                        length=item['length'],
                        qty_stem_flower=item['qty_stem_flower'],
                        stem_cost_price=item['stem_cost_price'],
                        profit_margin=item['margin'],
                    )

                # Actualizar totales de la orden
                order.qb_total += order_data['box_model'] == 'QB'
                order.hb_total += order_data['box_model'] == 'HB'
                order.total_price += order_item.line_price * order_item.qty_stem_flower
                order.save()

            return JsonResponse({'message': 'Order created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
