from django.urls import path

from .views import TemplateReportOrderView, PDFReportSupOrder


urlpatterns = [
    path('reports/order-supplier-template/<int:id_order>/', TemplateReportOrderView.as_view(), name='order_supplier_template'),
    path('reports/order-supplier/<int:id_order>/', PDFReportSupOrder.as_view(), name='report_supplier_order'),
]