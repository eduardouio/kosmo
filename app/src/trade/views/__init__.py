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
from .AprovePurchaseOrder import AprovePurchaseOrderView
from .CreateInvoiceByOrder import CreateInvoiceByOrder
from .CollectionsList import CollectionsList
from .PaymentsList import PaymentsList
from .DeleteInvoiceView import DeleteInvoiceView

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
    'AprovePurchaseOrderView',
    'CreateInvoiceByOrder',
    'CollectionsList',
    'PaymentsList',
    'DeleteInvoiceView',
]
