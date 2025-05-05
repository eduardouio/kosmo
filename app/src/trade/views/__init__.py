from .Stock import (
    StockDayListView,
    StockDayCreateView,
    StockDayDeleteView,
    StockDayDetailView,
)

from .StockDetail import (
    DetailStockDetail,
    SingleStockDetailUpdateView,
)

from .CustomerInvoiceList import CustomerInvoiceList
from .CustomerOrdersList import CustomerOrdersList
from .SupplierOrdersList import SupplierOrdersList
from .SupplierInvoiceList import SupplierInvoiceList
from .InvoiceDetailView import InvoiceDetailView
from .OrderDetailView import OrderDetailView
from .InvoiceFormView import InvoiceFormView

__all__ = [
    'StockDayListView',
    'StockDayCreateView',
    'StockDayDeleteView',
    'StockDayDetailView',
    'DetailStockDetail',
    'SingleStockDetailUpdateView',
    'CustomerInvoiceList',
    'CustomerOrdersList',
    'SupplierOrdersList',
    'SupplierInvoiceList',
    'InvoiceDetailView',
    'OrderDetailView',
    'InvoiceFormView',
]
