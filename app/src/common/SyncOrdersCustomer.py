from datetime import datetime
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import StockDetail
from partners.models import Partner
from datetime import datetime


class SyncOrdersCustomer:

    def sync_order_customer(self, order_supplier):

        if order_supplier.type_document != 'ORD_COMPRA':
            return False

        if order_supplier.parent_order.status != 'PENDIENTE':
            return False

        customer_order = order_supplier.parent_order
        customer_order.status = 'MODIFICADO'
        customer_order.save()
        OrderItems.delete_by_order(customer_order)

        all_supplier_orders = Order.get_by_parent_order(customer_order)

        for supplier_order in all_supplier_orders:
            supplier_orders_itms = OrderItems.get_by_order(supplier_order)
            for sup_ord_item in supplier_orders_itms:
                cus_order_item = OrderItems.objects.create(
                    order=customer_order,
                    box_model=sup_ord_item.box_model,
                    quantity=sup_ord_item.quantity,
                    id_stock_detail=sup_ord_item.id_stock_detail,
                    line_price=sup_ord_item.line_price,
                    tot_stem_flower=sup_ord_item.tot_stem_flower,
                    stem_cost_price=sup_ord_item.stem_cost_price,
                    profit_margin=sup_ord_item.profit_margin,
                    line_margin=sup_ord_item.line_margin,
                    line_total=sup_ord_item.line_total,
                )

                sup_box_items = OrderBoxItems.get_box_items(sup_ord_item)
                for sup_box_item in sup_box_items:
                    OrderBoxItems.objects.create(
                        order_item=cus_order_item,
                        product=sup_box_item.product,
                        qty_stem_flower=sup_box_item.qty_stem_flower,
                        stem_cost_price=sup_box_item.stem_cost_price,
                        profit_margin=sup_box_item.profit_margin,
                        line_margin=sup_box_item.line_margin,
                        line_total=sup_box_item.line_total,
                    )
        return True
