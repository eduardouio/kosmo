from django.urls import path
from api import (
    AnalizeStockTextAPI,
    StockDetailAPI,
    AllSuppliersAPI,
    DeleteStockDetailAPI,
    UpdateStockDetailAPI,
    AllProductsAPI,
    AddBoxItemAPI,
    AllCustomerAPI,
    CreateOrderAPI,
    OrderDetailAPI,
    UpdateCustmerOrderAPI,
    OrderPurchaseByOrderSale,
)

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
    path('api/partners/all-supliers/', AllSuppliersAPI.as_view(), name='all_supliers'),
    path('api/partners/all-customers/', AllCustomerAPI.as_view(), name='all_customers'),
    path('api/analize_stock_text/', AnalizeStockTextAPI.as_view(), name='analize_stock_text'),
    path('api/delete_stock_detail/', DeleteStockDetailAPI.as_view(), name='delete_stock_detail'),
    path('api/update_stock_detail/', UpdateStockDetailAPI.as_view(), name='update_stock_detail'),
    path('api/products/all_products/', AllProductsAPI.as_view(), name='all_products'),
    path('api/stock/add_box_item/', AddBoxItemAPI.as_view(), name='add_box_item'),
    path('api/orders/by_stock_day/<int:id_stock_day>/', OrderDetailAPI.as_view(), name='order_detail_by_stock_day'),
    path('api/orders/purchase_orders/<int:order_customer_id>/', OrderPurchaseByOrderSale.as_view(), name='purchase_by_order_sale'),
    path('api/orders/create-customer-order/', CreateOrderAPI.as_view(), name='create_order'),
    path('api/orders/update-customer-order/', UpdateCustmerOrderAPI.as_view(), name='update_order'),
]
