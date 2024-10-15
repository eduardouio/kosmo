from django.urls import path
from .views import StockDiary


urlpatterns = [
    path('trade/stock/add/', StockDiary.as_view(), name='add-stock'),
]
