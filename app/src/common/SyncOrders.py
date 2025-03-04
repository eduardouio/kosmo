from trade.models import OrderBoxItems, OrderItems, Order
from products.models import StockDetail
from common import loggin


class SyncOrders:

    @classmethod
    def sync(cls, order):
        if order.status in ['PENDIENTE', 'MODIFICADO']:

            # ORDER DE COMPRA Actualiza ordenes de proveedor
            if order.type_document == 'ORD_COMPRA':
                cls._sync_supplier_orders(order)

            # ORDER DE VENTA Actualiza orden de cliente
            cls._sync_customer_order(order)

        loggin(f"La orden {order.id} no se puede sincronizar", error=True)
        return False

    def _sync_customer_order(self, sup_order):
        loggin(f"Actualizando ordern del cliente {sup_order.id}")

    def _sync_supplier_orders(self, cus_order):
        loggin(f"Actualizando ordenes de proveedor {cus_order.id}")
        supplier_orders = Order.get_by_parent_order(cus_order)
        supplier_orders = [i for i in supplier_orders if i.status in ['PENDIENTE', 'MODIFICADO']]
        if supplier_orders is None:
            loggin(
                f"La orden {cus_order.id} no tiene ordenes de proveedor o estan cerradas", True
            )
            return False

        # detalles de orden de compra
        cus_order_items = OrderItems.get_by_order(cus_order.pk)
        order_items = []

        for cus_order_item in cus_order_items:
            stock_detail = StockDetail.get_by_id(
                cus_order_item.id_stock_detail
            )
            order_items.append({
                'supplier': stock_detail.partner,
                'order_item': cus_order_item,
                'box_items': OrderBoxItems.get_by_order_item(cus_order_item)
            })

        all_suppliers = list(set([i['supplier'] for i in order_items]))

        for sup_order in supplier_orders:
            if sup_order.partner not in all_suppliers:
                loggin(
                    f"La orden {sup_order.id} no tiene items asociados", True
                )
                sup_order.status = 'CANCELADO'
                sup_order.save()
                continue

            loggin(f"Actualizando orden de proveedor {sup_order.id}")

            self.update_suplier_order(
                sup_order,
                [i for i in order_items if i['supplier'] == sup_order.partner]
            )

    def update_suplier_order(self, sup_order , new_order_items):
        loggin(f"Actualizando orden de proveedor {sup_order.id}")
        old_order = {
            'sup_order': sup_order,
            'order_items': OrderItems.get_by_order(sup_order.pk)
        }
        
        