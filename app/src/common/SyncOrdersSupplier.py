from trade.models import OrderBoxItems, OrderItems, Order
from products.models import StockDetail


class SyncOrdersSupplier:

    def sync_order_customer(self, order_customer):

        if order_customer.type_document != 'ORD_VENTA':
            return False

        if order_customer.parent_order.status != 'PENDIENTE':
            return False

        sup_orders = Order.get_by_parent_order(order_customer)
        if len(sup_orders) == 0:
            self.create_supplier_orders(order_customer)
            return True

        self.update_supplier_orders(order_customer)

    def create_supplier_orders(self, order_customer):
        cus_order_items = OrderItems.get_by_order(order_customer)
        all_suppliers = []
        cus_ord_itms_by_supplier = []
        for c_ord_itm in cus_order_items:
            stock_detail = StockDetail.get_by_id(c_ord_itm.id_stock_detail)
            cus_ord_itms_by_supplier.append({
                'id_supplier': stock_detail.partner,
                'order_item': c_ord_itm
            })
            if stock_detail.partner not in all_suppliers:
                all_suppliers.append(stock_detail.partner)

        for supplier in all_suppliers:
            sup_order = Order.objects.create(
                partner=supplier,
                stock_day=order_customer.stock_day,
                type_document='ORD_COMPRA',
                parent_order=order_customer,
                status='PENDIENTE'
            )

            for cus_ord_it in cus_ord_itms_by_supplier:
                if cus_ord_it['id_supplier'].id == supplier.id:
                    sup_ord_itm = OrderItems.objects.create(
                        order=sup_order,
                        id_stock_detail=cus_ord_it['order_item'].id_stock_detail,
                        box_model=cus_ord_it['order_item'].box_model,
                        quantity=cus_ord_it['order_item'].quantity,
                    )

                    cus_box_items = OrderBoxItems.get_box_items(
                        cus_ord_it['order_item'])

                    for cus_box_item in cus_box_items:
                        OrderBoxItems.objects.create(
                            order_item=sup_ord_itm,
                            product=cus_box_item.product,
                            qty_stem_flower=cus_box_item.qty_stem_flower,
                            stem_cost_price=cus_box_item.stem_cost_price,
                            profit_margin=cus_box_item.profit_margin,
                            length=cus_box_item.length,
                        )
                    OrderItems.rebuild_order_item(sup_ord_itm)

            Order.rebuild_totals(sup_order)
        return True

    def update_supplier_orders(self, order_customer):
        cus_order_items = OrderItems.get_by_order(order_customer)
        all_suppliers = []
        cus_ord_itms_by_supplier = []
        for c_ord_itm in cus_order_items:
            stock_detail = StockDetail.get_by_id(c_ord_itm.id_stock_detail)
            cus_ord_itms_by_supplier.append({
                'id_supplier': stock_detail.partner,
                'order_item': c_ord_itm,
                'stock_detail': stock_detail
            })

            if stock_detail.partner not in all_suppliers:
                all_suppliers.append(stock_detail.partner)

        old_orders_suplier = Order.get_by_parent_order(order_customer)

        for i in old_orders_suplier:
            Order.disable_order_items(i)
            if i.partner not in all_suppliers:
                i.is_active = False
                i.save()

        for sup_order in [i for i in old_orders_suplier if i.is_active]:
            for cust_order_item in cus_ord_itms_by_supplier:
                if cust_order_item['id_supplier'].id == sup_order.partner.id:
                    new_order_item = OrderItems.objects.create(
                        order=sup_order,
                        id_stock_detail=cust_order_item['stock_detail'].id,
                        box_model=cust_order_item['order_item'].box_model,
                        quantity=cust_order_item['order_item'].quantity,
                    )
                    cus_box_item = OrderBoxItems.get_box_items(cust_order_item['order_item'])
                    for box_item in cus_box_item:
                        OrderBoxItems.objects.create(
                            order_item=new_order_item,
                            product=box_item.product,
                            qty_stem_flower=box_item.qty_stem_flower,
                            stem_cost_price=box_item.stem_cost_price,
                            profit_margin=box_item.profit_margin,
                            length=box_item.length
                        )
                    OrderItems.rebuild_order_item(new_order_item)
            Order.rebuild_totals(sup_order)

        Order.rebuild_totals(order_customer)
        return True
