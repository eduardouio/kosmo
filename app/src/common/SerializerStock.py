from products.models import BoxItems


class SerializerStock():

    def get_line(self, stock):
        item = {
            'stock_detail_id': stock.id,
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
                'short_name': stock.partner.short_name,
                'business_tax_id': stock.partner.business_tax_id,
                'address': stock.partner.address,
                'city': stock.partner.city,
                'default_profit_margin': float(stock.partner.default_profit_margin),
                'website': stock.partner.website,
                'credit_term': stock.partner.credit_term,
                'skype': stock.partner.skype,
                'email': stock.partner.email,
                'phone': stock.partner.phone,
                'is_active': stock.partner.is_active,
            },
            'box_items': [],
        }

        box_items = BoxItems.get_box_items(stock)
        for box in box_items:
            cost_product = box.stem_cost_price
            url_image = box.product.image.url if box.product.image else ''
            colors = box.product.colors.split(
                ',') if box.product.colors else []
            colors = [c.strip() for c in colors if c.strip()]
            item_box = {
                'id': box.id,
                'stock_detail_id': box.stock_detail_id,
                'product_id': box.product_id,
                'product_name': box.product.name,
                'product_variety': box.product.variety,
                'product_image': url_image,
                'product_colors': colors if colors else ['NO DEFINIDO'],
                'product_notes': box.product.notes,
                'length': box.length,
                'qty_stem_flower': box.qty_stem_flower,
                'stem_cost_price': float(cost_product),
                'margin': float(box.profit_margin),
                'is_active': box.is_active
            }
            item['box_items'].append(item_box)

        return item