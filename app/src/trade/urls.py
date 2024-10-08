from django.urls import path
from .views import StockDiary

app_name = 'trade'

urlpatterns = [
    path('trade/stock/add/', StockDiary.as_view(), name='add-stock'),
]
