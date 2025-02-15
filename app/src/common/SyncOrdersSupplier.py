from trade.models import OrderBoxItems, OrderItems, Order


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
        pass

    def update_supplier_orders(self, order_customer):
        pass
