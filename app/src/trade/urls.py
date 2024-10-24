from django.urls import path
from trade.views import StockDiary


urlpatterns = [    
    # trade
    path('trade/stock/add/', StockDiary.as_view(), name='stock-add'),
]
