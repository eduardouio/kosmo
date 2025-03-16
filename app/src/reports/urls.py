from django.urls import path

from .views import TemplateReportOrderView, PDFReportSupOrder


urlpatterns = [
    path('reports/order-template/<int:id_order>/', TemplateReportOrderView.as_view(), name='order_customer'),
    path('reports/order/<int:id_order>/', PDFReportSupOrder.as_view(), name='report_supplier_order'),
]