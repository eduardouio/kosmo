import json
from products.models import StockDetail
from trade.models import Order, OrderItems, OrderBoxItems


class SerializerOrder():

    def get_line(self, order_item):
        stock_detail = StockDetail.get_by_id(order_item.id_stock_detail)
        item = {
            'order_item_id': order_item.id,
            'id_stock_detail': order_item.id_stock_detail,
            'box_model': order_item.box_model,
            'quantity': order_item.quantity,
            'line_price': order_item.line_price,
            'line_margin': order_item.line_margin,
            'line_total': order_item.line_total,
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
                    'default_profit_margin': stock_detail.partner.default_profit_margin,
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

        box_items = OrderBoxItems.get_by_order_item(order_item)