from django.urls import path

from .views import (
    TemplateReportOrderSupView,
    PDFReportSupOrder,
    TemplateReportCusOrderView,
    PDFReportCusOrder)


urlpatterns = [
    path('reports/order-supplier-template/<int:id_order>/', TemplateReportOrderSupView.as_view(), name='order_supplier_template'),
    path('reports/order-supplier/<int:id_order>/', PDFReportSupOrder.as_view(), name='report_supplier_order'),
    path('reports/order-customer-template/<int:id_order>/', TemplateReportCusOrderView.as_view(), name='order_customer_template'),
    path('reports/order-customer/<int:id_order>/', PDFReportCusOrder.as_view(), name='report_customer_order'),
]