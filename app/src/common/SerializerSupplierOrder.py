from trade.models import OrderBoxItems


class SerializerSupplierOrder():

    def get_line(self, order_item):
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
                'total_bunches': box.total_bunches,
                'stems_bunch': box.stems_bunch,
                'is_active': box.is_active
            }
            item['box_items'].append(item_box)

        return item
