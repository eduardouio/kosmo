import json
from products.models import StockDetail
from trade.models import OrderBoxItems


class SerializerCustomerOrder():

    def get_line(self, order_item):
        stock_detail = StockDetail.get_by_id(order_item.id_stock_detail)
        item = {
            'order_item_id': order_item.id,
            'id_stock_detail': order_item.id_stock_detail,
            'box_model': order_item.box_model,
            'quantity': int(order_item.quantity),
            'line_price': float(order_item.line_price),
            'line_margin': float(order_item.line_margin),
            'line_total': float(order_item.line_total),
            'tot_stem_flower': order_item.tot_stem_flower,
            'is_active': order_item.is_active,
            'is_visible': True,
            'is_selected': False,
            'partner': {
                'partner': {
                    'id': stock_detail.partner.id,
                    'name': stock_detail.partner.name,
                    'short_name': stock_detail.partner.short_name,
                    'business_tax_id': stock_detail.partner.business_tax_id,
                    'address': stock_detail.partner.address,
                    'city': stock_detail.partner.city,
                    'default_profit_margin': float(
                        stock_detail.partner.default_profit_margin
                    ),
                    'website': stock_detail.partner.website,
                    'credit_term': stock_detail.partner.credit_term,
                    'skype': stock_detail.partner.skype,
                    'email': stock_detail.partner.email,
                    'phone': stock_detail.partner.phone,
                    'is_active': stock_detail.partner.is_active,
                },
            },
            'box_items': [],
        }

        box_items = OrderBoxItems.get_box_items(order_item)
        for box in box_items:
            cost_product = float(box.stem_cost_price)
            url_image = box.product.image.url if box.product.image else ''
            colors = box.product.colors.split(
                ',') if box.product.colors else []
            colors = [c.strip() for c in colors if c.strip()]
            item_box = {
                'id': box.id,
                'product_id': box.product_id,
                'product_name': box.product.name,
                'product_variety': box.product.variety,
                'product_image': url_image,
                'product_colors': colors if colors else ['NO DEFINIDO'],
                'product_notes': box.product.notes,
                'length': box.length,
                'qty_stem_flower': box.qty_stem_flower,
                'stem_cost_price': cost_product,
                'margin': float(box.profit_margin),
                'is_active': box.is_active
            }
            item['box_items'].append(item_box)

        return item