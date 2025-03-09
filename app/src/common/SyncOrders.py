from trade.models import OrderBoxItems, OrderItems, Order
from products.models import StockDetail
from common.AppLoger import loggin_event


class SyncOrders:

    def sync(self, order, create=False):
        if order.status in ['PENDIENTE', 'MODIFICADO']:
            # ORDER DE VENTA Actualiza ordenes de proveedor
            if order.type_document == 'ORD_VENTA':
                if create:
                    loggin_event(f"Creando orden de compra para {order.id}")
                    self._create_supplier_order(customer_order=order)
                else:
                    loggin_event(
                        f"Actualizando ordenes de proveedor para {order.id}")
                    self._sync_supplier_orders(cus_order=order)

            # ORDER DE COMPRA Actualiza orden de cliente
            self._sync_customer_order(sup_order=order)

    def _sync_customer_order(self, sup_order):
        loggin_event(f"Actualizando ordern del cliente {sup_order.id}")

    def _sync_supplier_orders(self, cus_order):
        loggin_event(f"Actualizando ordenes de proveedor {cus_order.id}")
        supplier_orders = Order.get_by_parent_order(cus_order.pk)
        customer_order_items = OrderItems.get_by_order(cus_order.pk)
        complete_customer_ord_items = []
        complete_supplier_orders = []
        order_customer_by_supplier = []
        all_suppliers = []

        # recuperamos el detalle de la venta asociado con proveedores y stock
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

            # lista unica de proveedores para las compras
            if stock_detail.partner not in all_suppliers:
                all_suppliers.append(stock_detail.partner)

        # agrupamos el detalle ordern de venta por proveedor
        for supplier in all_suppliers:
            new_item = {
                'review': False,  # para verificar si se reviso la orden
                'supplier': supplier,
                'order_items': []
            }
            for item in complete_customer_ord_items:
                if item['supplier'] == supplier:
                    new_item['order_items'].append(item['order_item'])
            order_customer_by_supplier.append(new_item)

        for sup_order in supplier_orders:
            complete_supplier_orders.append({
                'order': sup_order,
                'supplier': sup_order.partner,
                'order_items': OrderItems.get_by_order(sup_order.pk)
            })
        self.compare_orders(
            complete_supplier_orders,
            order_customer_by_supplier,
            all_suppliers
        )

    def compare_orders(
            self,
            complete_supplier_orders,
            order_customer_by_supplier,
            all_suppliers):
        loggin_event("Comparando ordenes de compra existentes con nuevas")

        # verificamos si todas las ordenes de compra estan completas
        orders_to_remove = []
        for sup_order in complete_supplier_orders:
            if sup_order['supplier'] not in all_suppliers:
                loggin_event(
                    f"La order de compra {sup_order.id} no esta en la venta"
                )
                loggin_event("Se cancela la orde de compra")
                sup_order.status = 'CANCELADO'
                sup_order.save()
                orders_to_remove.append(sup_order)

        # eliminamos las ordenes de compra que no estan en la venta
        for order in orders_to_remove:
            complete_supplier_orders.remove(order)

        # verificamos si actualizamos cada orden de compra
        for new_sup_order in order_customer_by_supplier:
            for old_sup_order in complete_supplier_orders:
                if new_sup_order['supplier'] == old_sup_order['supplier']:
                    new_sup_order['review'] = True
                    self._update_supplier_order(
                        new_sup_order,
                        old_sup_order
                    )

        # creamos las ordenes de compra que no existen
        for new_sup_order in order_customer_by_supplier:
            if not new_sup_order['review']:
                new_sup_order['review'] = True
                self._create_supplier_order(new_sup_order)

    def _update_supplier_order(self, new_sup_order, old_sup_order):
        import ipdb
        ipdb.set_trace()

    def _create_supplier_order(self, customer_order):
        loggin_event(f"Creando orden de compra para {customer_order}")
        cus_order_items = OrderItems.get_by_order(customer_order)
        details_by_supplier = []

        for ord in cus_order_items:
            stock_detail = StockDetail.get_by_id(ord.id_stock_detail)
            if stock_detail.partner not in [i['supplier'] for i in details_by_supplier]:
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
                parent_order=customer_order
            )
            for ord in supplier['order_items']:
                ord_item = OrderItems.objects.create(
                    order=sup_order,
                    id_stock_detail=ord.id_stock_detail,
                    box_model=ord.box_model,
                    quantity=ord.quantity
                )

                cus_ord_box_items = OrderBoxItems.get_by_order_item(ord)
                for box_item in cus_ord_box_items:
                    OrderBoxItems.objects.create(
                        order_item=ord_item,
                        product=box_item.product,
                        length=box_item.length,
                        qty_stem_flower=box_item.qty_stem_flower,
                        stem_cost_price=box_item.stem_cost_price,
                        profit_margin=box_item.profit_margin
                    )
            Order.rebuild_totals(sup_order)
            loggin_event(f"Orden de compra {sup_order.id} creada con exito")
