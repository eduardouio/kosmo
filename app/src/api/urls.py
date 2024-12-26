from django.urls import path
from .StockDetailAPI import StockDetailAPI
from .AllSuppliersAPI import AllSuppliersAPI

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
    path('api/partners/all-supliers/', AllSuppliersAPI.as_view(), name='all_supliers'),
]
