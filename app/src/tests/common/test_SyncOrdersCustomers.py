import pytest
from common import SyncOrdersCustomer
from trade.models import Order, OrderBoxItems, OrderItems


@pytest.mark.django_db
class TestSyncOrdersCustomers:

    @pytest.fixture
    def sync_orders_customers(self):
        return SyncOrdersCustomer()

    def test_sync_orders_customers(self, sync_orders_customers):
        order_data = {
            'supplier_order': Order.get_order_by_id(3),
            'order_items': OrderItems.get_by_order(3),
        }

        for order_item in order_data['order_items']:
            if order_item.id == 12:
                order_item.delete()
                break

            order_item.qty_stem_flower = 10

        sync_orders_customers.sync_order_customer(order_data['supplier_order'])

        new_ordes_items = OrderItems.get_by_order(3)
        order_customer = Order.get_order_by_id(order_data.parent_order.id)
        assert len(new_ordes_items) == 2
        assert order_customer.status == 'MODIFICADO'

    def test_by_customer_order(self, sync_orders_customers):
        result = sync_orders_customers.sync_order_customer(
            Order.get_order_by_id(3)
        )

        assert not result
