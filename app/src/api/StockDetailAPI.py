from django.http import JsonResponse
from django.views import View
from products.models import StockDetail, StockDay, BoxItems
from trade.models import Order


class StockDetailAPI(View):
    def get(self, request, stock_day_id):
        stock_day = StockDay.get_by_id(stock_day_id)
        if not stock_day:
            return JsonResponse(
                {
                    'error': 'No hay detalles para esta diponibilidad, debe importar primero'
                },
                status=404
            )

        stock_details = StockDetail.get_by_stock_day(stock_day)
        if not stock_details:
            return JsonResponse(
                {
                    'error': 'No hay detalles para esta diponibilidad, debe importar primero'
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
                'is_visible': True,
                'is_selected': False,
                'is_in_order': False,
                'box_model': stock.box_model,
                'tot_stem_flower': stock.tot_stem_flower,
                'tot_cost_price_box': float(stock.tot_cost_price_box),
                'id_user_created': stock.id_user_created,
                'is_active': stock.is_active,
                'partner': {
                    'id': stock.partner.id,
                    'name': stock.partner.name,
                    'business_tax_id': stock.partner.business_tax_id,
                    'address': stock.partner.address,
                    'city': stock.partner.city,
                    'default_profit_margin': stock.partner.default_profit_margin,
                    'website': stock.partner.website,
                    'credit_term': stock.partner.credit_term,
                    'skype': stock.partner.skype,
                    'email': stock.partner.email,
                    'phone': stock.partner.phone,
                    'is_active': stock.partner.is_active,
                },
            }

            for box in box_items:
                cost_product = float(box.stem_cost_price)
                url_image = box.product.image.url if box.product.image else ''
                colors = box.product.colors.split(
                    ',') if box.product.colors else []
                item_box = {
                    'id': box.id,
                    'stock_detail_id': box.stock_detail_id,
                    'product_id': box.product_id,
                    'product_name': box.product.name,
                    'product_variety': box.product.variety,
                    'product_image': url_image,
                    'product_colors': colors,
                    'product_notes': box.product.notes,
                    'length': box.length,
                    'qty_stem_flower': box.qty_stem_flower,
                    'stem_cost_price': cost_product,
                    'margin': box.profit_margin,
                    'is_active': box.is_active
                }
                item['box_items'].append(item_box)

            result_dict.append(item)

        stock_day = StockDay.get_by_id(stock_day_id)
        orders = Order.get_orders_by_stock_day(stock_day)
        return JsonResponse(
            {
                'stock': result_dict,
                'stockDay': {
                    'id': stock_day.id,
                    'date': stock_day.date,
                    'is_active': stock_day.is_active,
                },
                'orders': [o.id for o in orders],
            },
            status=200
        )
