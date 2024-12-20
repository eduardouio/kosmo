from django.urls import path
from .StockDetailAPI import StockDetailAPI

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
]
