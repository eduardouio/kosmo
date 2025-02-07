from datetime import datetime
from products.models import StockDetail
from trade.models import Order, OrderBoxItems, OrderItems
from partners.models import Partner
from django.db import transaction
from datetime import datetime


class CreateOrUpdateOrderSupplier:

    # @transaction.atomic
    def create_or_update(self, customer_order, order_details):

        order_data = []
        suppliers = set(
            [i['partner']['partner']['id'] for i in order_details]
        )

        # agrupamos el pedido por clientes
        for supplier in suppliers:
            my_supplier = Partner.get_partner_by_id(supplier)
            details_sup_order = [
                i for i in order_details
                if i['partner']['partner']['id'] == supplier
            ]
            order_data.append(
                {
                    'supplier': my_supplier,
                    'details': details_sup_order,
                }
            )
        existing_orders = Order.get_by_sale_order(customer_order)

        if not existing_orders:
            self.create_suplier_orders(customer_order, order_data)

        for existing_order in existing_orders:
            if existing_order.status != 'PENDIENTE':
                raise Exception(
                    'No se puede modificar un pedido que no esta pendiente'
                )

            self.update_suplier_orders(
                customer_order, existing_order, order_data
            )

    def create_suplier_orders(self, customer_order, order_data):
        for itm_order in order_data:
            purchase_order = Order.objects.create(
                stock_day_id=customer_order.stock_day.id,
                date=datetime.now(),
                partner=itm_order['supplier'],
                type_document="ORD_COMPRA",
                parent_order=customer_order,
                status="PENDIENTE"
            )
            for order_detail in itm_order['details']:
                order_item = OrderItems.objects.create(
                    order=purchase_order,
                    id_stock_detail=order_detail['id_stock_detail'],
                    box_model=order_detail['box_model'],
                    quantity=order_detail['quantity'],
                )
                for box_item in order_detail['box_items']:
                    OrderBoxItems.objects.create(
                        order_item=order_item,
                        product_id=box_item['product_id'],
                        length=box_item['length'],
                        qty_stem_flower=box_item['qty_stem_flower'],
                        stem_cost_price=box_item['stem_cost_price'],
                        profit_margin=float(box_item['margin'])
                    )

    def update_suplier_orders(self, customer_order, existing_order, order_data):
        pass