from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems
from products.models import StockDetail
from partners.models import Partner
import json
from decimal import Decimal


class CreateOrderAPI(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            # Validate required fields
            required_fields = ['partner_id', 'type_document', 'items']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing required field: {field}'}, status=400)

            # Get partner
            partner = Partner.objects.filter(id=data['partner_id']).first()
            if not partner:
                return JsonResponse({'error': 'Partner not found'}, status=404)

            # Create order
            order = Order.objects.create(
                partner=partner,
                type_document=data['type_document'],
                status='PENDIENTE',
                num_order=data.get('num_order'),
                delivery_date=data.get('delivery_date'),
                discount=data.get('discount', 0)
            )

            # Process order items
            total_price = Decimal('0.00')
            qb_total = 0
            hb_total = 0

            for item in data['items']:
                stock_detail = StockDetail.objects.filter(
                    id=item['stock_detail_id']).first()
                if not stock_detail:
                    order.delete()
                    return JsonResponse({'error': f'Stock detail not found: {item["stock_detail_id"]}'}, status=404)

                # Calculate line price with margin
                line_price = (
                    stock_detail.stem_cost_price_box
                    * stock_detail.tot_stem_flower
                    * Decimal('1.06')
                )

                # Create order item
                order_item = OrderItems.objects.create(
                    order=order,
                    stock_detail=stock_detail,
                    line_price=line_price,
                    qty_stem_flower=stock_detail.tot_stem_flower,
                    box_model=item.get('box_model', 'QB'),
                    tot_stem_flower=stock_detail.tot_stem_flower,
                    tot_cost_price_box=stock_detail.stem_cost_price_box,
                    profit_margin=Decimal('0.06')
                )

                total_price += line_price
                if order_item.box_model == 'QB':
                    qb_total += 1
                elif order_item.box_model == 'HB':
                    hb_total += 1

            # Update order totals
            order.total_price = total_price
            order.qb_total = qb_total
            order.hb_total = hb_total
            order.save()

            return JsonResponse({
                'message': 'Order created successfully',
                'order_id': order.id,
                'total_price': float(total_price),
                'qb_total': qb_total,
                'hb_total': hb_total
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
