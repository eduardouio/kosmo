from trade.models import OrderBoxItems, OrderItems, Order
from products.models import StockDetail
from common.AppLoger import loggin_event


class SyncOrders:

    def sync_suppliers(self, order, create=False):
        if order.status in ['PENDIENTE', 'MODIFICADO']:
            if order.type_document == 'ORD_VENTA':
                if create:
                    loggin_event(f"Creando orden de compra para {order.id}")
                    self._create_supplier_order(customer_order=order)
                else:
                    loggin_event(
                        f"Actualizando ordenes de proveedor para {order.id}")
                    self._sync_supplier_orders(cus_order=order)

    def sync_customer(self, sup_order):
        loggin_event(f"Actualizando ordern del cliente {sup_order.id}")
        cus_order = Order.get_order_by_id(sup_order.parent_order.id)

        [
            OrderItems.disable_by_order_item(item)
            for item in OrderItems.get_by_supplier(
                cus_order, sup_order.partner
            )
        ]

        sup_order_items = OrderItems.get_by_order(sup_order)
        if cus_order.status not in ['PENDIENTE', 'MODIFICADO']:
            loggin_event(
                f"La orden de venta {cus_order.id} no se puede modificar"
            )
            raise Exception(
                f"La orden de venta {cus_order.id} no se puede modificar"
            )

        
        for sup_item in sup_order_items:
            new_order_item = OrderItems.objects.create(
                order=cus_order,
                id_stock_detail=sup_item.id_stock_detail,
                line_price=sup_item.line_price,
                line_margin=sup_item.line_margin,
                line_total=sup_item.line_total,
                tot_stem_flower=sup_item.tot_stem_flower,
                total_bunches=sup_item.total_bunches,  
                box_model=sup_item.box_model,
                quantity=sup_item.quantity
            )
            for box in OrderBoxItems.get_by_order_item(sup_item):

                OrderBoxItems.objects.create(
                    order_item=new_order_item,
                    product=box.product,
                    length=box.length,
                    qty_stem_flower=box.qty_stem_flower,
                    stem_cost_price=box.stem_cost_price,
                    profit_margin=box.profit_margin,
                    total_bunches=box.total_bunches,  
                    stems_bunch=box.stems_bunch       
                )

        cus_order.status = 'MODIFICADO'
        cus_order.save()
        Order.rebuild_totals(cus_order)
        return True

    def _sync_supplier_orders(self, cus_order):
        loggin_event(f"Actualizando ordenes de proveedor {cus_order.id}")
        old_supplier_orders = Order.get_by_parent_order(cus_order.pk)
        customer_order_items = OrderItems.get_by_order(cus_order.pk)
        complete_customer_ord_items = []
        old_complete_supplier_orders = []
        order_customer_by_supplier = []
        all_suppliers = []

        
        for order_item in customer_order_items:
            stock_detail = StockDetail.get_by_id(
                order_item.id_stock_detail
            )
            complete_customer_ord_items.append({
                'supplier': stock_detail.partner,
                'order_item': order_item,
                'stock_detail': stock_detail,
                'box_items': OrderBoxItems.get_by_order_item(order_item)
            })

            
            if stock_detail.partner not in all_suppliers:
                all_suppliers.append(stock_detail.partner)

        
        for supplier in all_suppliers:
            new_item = {
                'supplier': supplier,
                'order_items': []
            }
            for item in complete_customer_ord_items:
                if item['supplier'] == supplier:
                    new_item['order_items'].append(item['order_item'])
            order_customer_by_supplier.append(new_item)

        for sup_order in old_supplier_orders:
            if sup_order.status not in ['CANCELADO']:
                old_complete_supplier_orders.append({
                    'order': sup_order,
                    'supplier': sup_order.partner,
                    'order_items': OrderItems.get_by_order(sup_order.pk)
                })

        self.compare_orders(old_complete_supplier_orders,
                            order_customer_by_supplier,
                            all_suppliers
                            )

    def compare_orders(
            self,
            old_complete_supplier_orders,
            order_customer_by_supplier,
            all_suppliers):
        loggin_event("Comparando ordenes de compra existentes con nuevas")

        
        orders_to_remove = []
        for sup_order in old_complete_supplier_orders:
            if sup_order['supplier'] not in all_suppliers:
                loggin_event(
                    f"La order de compra {sup_order.id} no esta en la venta"
                )
                loggin_event("Se cancela la orde de compra")
                sup_order.status = 'CANCELADO'
                sup_order.save()
                orders_to_remove.append(sup_order)

        for new_sup_order in order_customer_by_supplier:
            old_order = self._get_order_by_su(
                old_complete_supplier_orders, new_sup_order['supplier']
            )
            self._compare_orders(new_sup_order, old_order)

    def _get_order_by_su(self, old_complete_supplier_orders, suplier):
        for sup_order in old_complete_supplier_orders:
            if sup_order['supplier'] == suplier:
                return sup_order
        raise Exception(f"La orden de compra {suplier} no existe")

    def _compare_orders(self, new_order, old_order):
        my_order = old_order['order']
        new_order_items = new_order['order_items']
        old_order_items = old_order['order_items']

        if len(new_order_items) != len(old_order_items):
            my_order.status = 'MODIFICADO'
            my_order.save()
            self._create_order_items(new_order_items, my_order)
            return True

        for new_itm, old_itm in zip(new_order_items, old_order_items):
            if self._comparte_items(new_itm, old_itm):
                my_order.status = 'MODIFICADO'
                my_order.save()
                self._create_order_items(new_order_items, my_order)
                return True

    def _comparte_items(self, new_itm, old_itm):
        if new_itm.id_stock_detail != old_itm.id_stock_detail:
            return True
        if new_itm.box_model != old_itm.box_model:
            return True
        if new_itm.quantity != old_itm.quantity:
            return True
        if new_itm.tot_stem_flower != old_itm.tot_stem_flower:
            return True
        if new_itm.line_margin != old_itm.line_margin:
            return True
        if new_itm.line_price != old_itm.line_price:
            return True
        if new_itm.line_total != old_itm.line_total:
            return True
        return False

    def _create_order_items(self, new_order_items, my_order):
        Order.disable_order_items(my_order)
        for new_item in new_order_items:
            my_order_item = OrderItems.objects.create(
                order=my_order,
                id_stock_detail=new_item.id_stock_detail,
                box_model=new_item.box_model,
                quantity=new_item.quantity,
                tot_stem_flower=new_item.tot_stem_flower,
                total_bunches=new_item.total_bunches,  
                line_margin=new_item.line_margin,
                line_price=new_item.line_price,
                line_total=new_item.line_total
            )
            self._create_order_box_items(new_item, my_order_item)

    def _create_order_box_items(self, new_item, my_order_item):
        for box_item in OrderBoxItems.get_by_order_item(new_item):
            OrderBoxItems.objects.create(
                order_item=my_order_item,
                product=box_item.product,
                length=box_item.length,
                qty_stem_flower=box_item.qty_stem_flower,
                stem_cost_price=box_item.stem_cost_price,
                profit_margin=box_item.profit_margin,
                total_bunches=box_item.total_bunches,  
                stems_bunch=box_item.stems_bunch       
            )

    def _update_supplier_order(self, new_sup_order, old_sup_order):
        loggin_event(
            f"Actualizando orden de compra {old_sup_order['order'].id}")
        current_order = old_sup_order['order']
        current_order.status = 'MODIFICADO'
        current_order.save()
        OrderItems.disable_by_order(current_order)
        new_orders_items = new_sup_order['order_items']
        for new_order_item in new_orders_items:
            my_order_item = OrderItems.objects.create(
                order=current_order,
                id_stock_detail=new_order_item.id_stock_detail,
                box_model=new_order_item.box_model,
                quantity=new_order_item.quantity,
                tot_stem_flower=new_order_item.tot_stem_flower,  
                total_bunches=new_order_item.total_bunches       
            )
            self._create_order_box_items(new_order_item, my_order_item)
        Order.rebuild_totals(current_order)

    def _create_supplier_order(self, customer_order):
        loggin_event(f"Creando orden de compra para {customer_order}")
        cus_order_items = OrderItems.get_by_order(customer_order)
        details_by_supplier = []

        for ord in cus_order_items:
            stock_detail = StockDetail.get_by_id(ord.id_stock_detail)
            _ = [i['supplier'] for i in details_by_supplier]
            if stock_detail.partner not in _:
                details_by_supplier.append({
                    "supplier": stock_detail.partner,
                    "order_items": []
                })

        for ord in cus_order_items:
            stock_detail = StockDetail.get_by_id(ord.id_stock_detail)
            for ord_sup in details_by_supplier:
                if ord_sup['supplier'] == stock_detail.partner:
                    ord_sup['order_items'].append(ord)

        loggin_event(f"Proveedores {details_by_supplier}")

        for supplier in details_by_supplier:
            sup_order = Order.objects.create(
                partner=supplier['supplier'],
                stock_day=customer_order.stock_day,
                type_document='ORD_COMPRA',
                status='PENDIENTE',
                parent_order=customer_order,
                serie='200',  
                consecutive=Order.get_next_purchase_consecutive(),  
                delivery_date=customer_order.delivery_date,  
                num_order=customer_order.num_order  
            )
            for ord in supplier['order_items']:
                ord_item = OrderItems.objects.create(
                    order=sup_order,
                    id_stock_detail=ord.id_stock_detail,
                    box_model=ord.box_model,
                    quantity=ord.quantity,
                    tot_stem_flower=ord.tot_stem_flower,  
                    total_bunches=ord.total_bunches       
                )
                self._create_order_box_items(ord, ord_item)
            Order.rebuild_totals(sup_order)
            loggin_event(f"Orden de compra {sup_order.id} creada con éxito - Serie: {sup_order.serie}, Consecutivo: {sup_order.consecutive}")

    def cancell_supplier_orders(self, order):
        loggin_event(f"Cancelando orden de compra {order.id}")
        if order.status in ['FACTURADO', 'CANCELADO']:
            return False
        order_suplier = Order.get_by_parent_order(order.pk)
        for order_sup in order_suplier:
            order_sup.status = 'CANCELADO'
            order_sup.save()
        order.status = 'CANCELADO'
        order.save()
        return True
