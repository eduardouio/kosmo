from trade.models import OrderBoxItems, OrderItems


class SyncOrdersCustomer:

    def sync_order_customer(self, order_supplier):

        if order_supplier.type_document != 'ORD_COMPRA':
            return False

        if order_supplier.parent_order.status != 'PENDIENTE':
            return False

        customer_order = order_supplier.parent_order
        customer_order.status = 'MODIFICADO'
        customer_order.save()

        sup_ord_itms = OrderItems.get_by_order(order_supplier)
        cus_ord_itms = OrderItems.get_by_supplier(
            customer_order, order_supplier.partner
        )

        [cus_ord_itm.disable_order_item() for cus_ord_itm in cus_ord_itms]

        for sup_ord_item in sup_ord_itms:
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
