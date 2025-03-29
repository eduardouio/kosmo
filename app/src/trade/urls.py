from django.urls import path
from trade.views import (
    StockDayListView,
    StockDayCreateView,
    StockDayDeleteView,
    StockDayDetailView,
    DetailStockDetail,
    SingleStockDetailUpdateView,
    CustomerInvoiceList,
    CustomerOrdersList,
    SupplierOrdersList,
    SupplierInvoiceList,
    InvoiceDetailView,
    OrderDetailView,
)


urlpatterns = [    
    path('trade/stock/', StockDayListView.as_view(), name='stock_list'),
    path('trade/stock/<int:pk>/', StockDayDetailView.as_view(), name='stock_detail'),
    path('trade/stock/nuevo/', StockDayCreateView.as_view(), name='stock_create'),
    path('trade/stock/eliminar/<int:pk>/', StockDayDeleteView.as_view(), name='stock_delete'),
    path('trade/stock/detalle/<int:pk>/', DetailStockDetail.as_view(), name='stock_detail_detail'),
    path('trade/stock/detalle/actualizar/<int:pk>/', SingleStockDetailUpdateView.as_view(), name='stock_detail_update'),
    path('trade/customer-invoices/', CustomerInvoiceList.as_view(), name='customer_invoice_list'),
    path('trade/customer-orders/', CustomerOrdersList.as_view(), name='customer_orders_list'),
    path('trade/supplier-orders/', SupplierOrdersList.as_view(), name='supplier_orders_list'),    
    path('trade/supplier-invoices/', SupplierInvoiceList.as_view(), name='supplier_invoice_list'),
    path('trade/invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('trade/order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
]
