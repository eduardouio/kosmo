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
    path('api/order/create_order/', CreateOrderAPI.as_view(), name='create_order'),
    path('api/order/<int:id_order>/', OrderDetailAPI.as_view(), name='order_detail'),
]
