from datetime import datetime
from trade.models import Order, OrderBoxItems, OrderItems
from products.models import StockDetail
from partners.models import Partner
from datetime import datetime


class SyncOrdersSupplier:

    def sync(self, order, order_items):
        if order.type_document != 'ORD_COMPRA':
            return False
        
        stock_details = [
            StockDetail.get_by_id(i) for i in order_items
        ]
    

    def create_supplier_order(self, order, supplier, order_items):
        pass