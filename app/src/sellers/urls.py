from django.urls import path
from .views.SellerHomeView import SellerHomeView
from .views.SellerStockView import SellerStockView
from .views.SellerOrdersView import SellerOrdersView
from .views.SellerCreateOrderView import (
    SellerCreateOrderView,
    SellerEditOrderView
)
from .views.SellerInvoiceView import SellerInvoiceView
from .views.api_views import get_customers_api, create_order_api

app_name = 'sellers'

urlpatterns = [
    # Dashboard principal
    path('', SellerHomeView.as_view(), name='home'),
    # Stocks/Disponibilidades
    path('stocks/', SellerStockView.as_view(), name='stocks'),
    # Órdenes de venta
    path('orders/', SellerOrdersView.as_view(), name='orders'),
    path('orders/create/', SellerCreateOrderView.as_view(), name='create_order'),
    path('orders/<int:pk>/edit/', SellerEditOrderView.as_view(), name='edit_order'),

    # Facturas
    path('invoices/', SellerInvoiceView.as_view(), name='invoices'),
    
    # APIs
    path('api/customers/', get_customers_api, name='api_customers'),
    path('api/orders/create/', create_order_api, name='api_create_order'),
]

