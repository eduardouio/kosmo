from django.urls import path
from trade.views import Stock


urlpatterns = [    
    path('trade/stock/nuevo/', Stock.as_view(), name='stock-add'),
]
