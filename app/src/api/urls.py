from django.urls import path
from api import AnalizeStockText, StockDetailAPI, AllSuppliersAPI

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
    path('api/partners/all-supliers/', AllSuppliersAPI.as_view(), name='all_supliers'),
    path('api/analize_stock_text/', AnalizeStockText.as_view(), name='analize_stock_text'),
]
