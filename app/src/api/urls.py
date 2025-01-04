from django.urls import path
from api import (
    AnalizeStockText,
    StockDetailAPI,
    AllSuppliersAPI,
    DeleteStockDetailAPI,
    UpdateStockDetailAPI
)

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
    path('api/partners/all-supliers/', AllSuppliersAPI.as_view(), name='all_supliers'),
    path('api/analize_stock_text/', AnalizeStockText.as_view(), name='analize_stock_text'),
    path('api/delete_stock_detail/', DeleteStockDetailAPI.as_view(), name='delete_stock_detail'),
    path('api/update_stock_detail/', UpdateStockDetailAPI.as_view(), name='update_stock_detail'),
]
