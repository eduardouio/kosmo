from django.urls import path
from trade.views import (
    StockDayListView,
    StockDayCreateView,
    StockDayDeleteView,
    StockDayDetailView,
)


urlpatterns = [    
    path('trade/stock/', StockDayListView.as_view(), name='stock_list'),
    path('trade/stock/<int:pk>/', StockDayDetailView.as_view(), name='stock_detail'),
    path('trade/stock/nuevo/', StockDayCreateView.as_view(), name='stock_create'),
    path('trade/stock/eliminar/<int:pk>/', StockDayDeleteView.as_view(), name='stock_delete'),
]
