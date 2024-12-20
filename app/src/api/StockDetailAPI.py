import json
from django.http import JsonResponse
from django.views import View
from products.models import StockDetail, StockDay, BoxItems


class StockDetailAPI(View):
    def get(self, request, stock_day_id):
        stock_day = StockDay.get_by_id(stock_day_id)
        if not stock_day:
            return JsonResponse(
                {
                    'error': 'Stock day not found'
                },
                status=404
            )

        stock_details = StockDetail.get_by_stock_day(stock_day)
        if not stock_details:
            return JsonResponse(
                {
                    'error': 'Stock details not found'
                },
                status=404
            )

        result_dict = []

        for stock in stock_details:
            box_items = BoxItems.get_box_items(stock)
            item = {
                'stock_detail_id': stock.id,
                'box_items': [],
                'quantity': stock.quantity,
                'box_model': stock.box_model,
                'tot_stem_flower': stock.tot_stem_flower,
                'stem_cost_price_box': float(stock.stem_cost_price_box),
                'id_user_created': stock.id_user_created,
                'is_active': stock.is_active,
                'parner': {
                    'id': stock.partner.id,
                    'name': stock.partner.name,
                    'business_tax_id': stock.partner.business_tax_id,
                    'address': stock.partner.address,
                    'city': stock.partner.city,
                    'default_profit_margin': float(stock.partner.default_profit_margin),
                    'is_profit_margin_included': float(stock.partner.is_profit_margin_included),
                    'website': stock.partner.website,
                    'credit_term': stock.partner.credit_term,
                    'skype': stock.partner.skype,
                    'email': stock.partner.email,
                    'phone': stock.partner.phone,
                    'is_active': stock.partner.is_active,
                },
            }

            for box in box_items:
                item_box = {
                    'id': box.id,
                    'stock_detail_id': box.stock_detail_id,
                    'product_id': box.product_id,
                    'product_name': box.product.name,
                    'product_variety': box.product.variety,
                    'product_image': box.product.image.url if box.product.image else '',
                    'product_colors': box.product.colors,
                    'product_default_profit_margin': float(box.product.default_profit_margin),
                    'product_notes': box.product.notes,
                    'length': box.length,
                    'qty_stem_flower': box.qty_stem_flower,
                    'stem_cost_price': float(box.stem_cost_price),
                    'is_active': box.is_active
                }
                item['box_items'].append(item_box)

            result_dict.append(item)
        return JsonResponse(
            {
                'stock': result_dict
            },
            status=200
        )
