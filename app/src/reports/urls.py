from django.urls import path

from .views import PDFOrderCustomer, PDFTest


urlpatterns = [
    path('reports/order/<int:id_order>/', PDFOrderCustomer.as_view(), name='order_customer'),
    path('reports/test/', PDFTest.as_view(), name='test'),
]