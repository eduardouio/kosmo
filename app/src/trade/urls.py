from django.urls import path
from trade.views import (
    StockDayListView,
    StockDayCreateView,
    StockDayDeleteView,
    StockDayDetailView,
    DetailStockDetail,
    SingleStockDetailUpdateView,
    CustomerInvoiceList,
    CustomerOrdersList,
    SupplierOrdersList,
    SupplierInvoiceList,
    OrderDetailView,
    InvoiceDetailView,
    InvoiceFormView,
    AprovePurchaseOrderView,
    CreateInvoiceByOrder,
    CollectionsListView,
    PaymentsList,
    DeleteInvoiceView,
    SupplierInvoiceDetail,
    InvoiceSupplierUpdate,
    BatchOrderApprovalView,
    PaymentFormView,
    CollectionFormView,
    PaymentDetailView,
    CollectionDetailView,
)

# Importar APIs
from api.trade import (
    CollectionsCreateUpdateAPI,
    CollectionsVoidAPI,
    CollectionsContextAPI,
    PaymentCreateUpdateAPI,
    PaymentVoidAPI,
)
from api.trade.CreditNoteAPI import CreditNoteInvoicesAPI

from trade.views.CreateCreditNote import CreditNoteCreateView
from trade.views.DetailCreditNote import CreditNoteDetailView
from trade.views.CreditNoteListView import CreditNoteListView
from trade.views.DeleteCreditNote import CreditNoteVoidView

urlpatterns = [
	# stocks
    path('trade/<int:pk>/', DetailStockDetail.as_view(), name='stock_detail_detail'),
    path('trade/stock/', StockDayListView.as_view(), name='stock_list'),
    path('trade/stock/<int:pk>/', StockDayDetailView.as_view(), name='stock_detail'),
    path('trade/stock/nuevo/', StockDayCreateView.as_view(), name='stock_create'),
    path('trade/stock/eliminar/<int:pk>/', StockDayDeleteView.as_view(), name='stock_delete'),
    path('trade/stock/detalle/actualizar/<int:pk>/', SingleStockDetailUpdateView.as_view(), name='stock_detail_update'),
	# parners
    path('trade/customer-invoices/', CustomerInvoiceList.as_view(), name='customer_invoice_list'),
    path('trade/supplier-invoices/', SupplierInvoiceList.as_view(), name='supplier_invoice_list'),
    path('trade/supplier-invoice/update/<int:invoice_id>/', InvoiceSupplierUpdate.as_view(), name='invoice_supplier_update'),
	# invoices
    path('trade/invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail_presentation'),
    path('trade/invoice-form/<int:pk>/', InvoiceFormView.as_view(), name='edit_invoice_form'),
    path('trade/invoice/update/<int:pk>/', InvoiceFormView.as_view(), name='update_invoice'),
    path('trade/invoice/delete/<int:pk>/', DeleteInvoiceView.as_view(), name='delete_invoice'),
    path('trade/supplier-invoice/<int:invoice_id>/', SupplierInvoiceDetail.as_view(), name='supplier_invoice_detail'),
	# orders
    path('trade/order/<int:pk>/', OrderDetailView.as_view(), name='order_detail_presentation'),
    path('trade/customer-orders/', CustomerOrdersList.as_view(), name='customer_orders_list'),
    path('trade/supplier-orders/', SupplierOrdersList.as_view(), name='supplier_orders_list'),
    path('trade/order/aprove/<int:pk>/', AprovePurchaseOrderView.as_view(), name='aprove_purchase_order'),
    path('trade/aprove-batch-orders/', BatchOrderApprovalView.as_view(), name='aprove_batch_orders'),
    path('trade/order/generate-invoice/<int:pk>/', CreateInvoiceByOrder.as_view(), name='generate_invoice_by_order'),
	# payments
    path('pagos/', PaymentsList.as_view(), name="payments_list"),
    path('pagos/nuevo/', PaymentFormView.as_view(), name='payment_create'),
	# collections
    path('cobros/', CollectionsListView.as_view(), name='collections_list'),
    path('cobros/nuevo/', CollectionFormView.as_view(), name='collect_form'),
    path('cobros/editar/<int:collection_id>/', CollectionFormView.as_view(), name='collection_form'),
    path('trade/collection/<int:pk>/', CollectionDetailView.as_view(), name='collection_detail'),
	#api 
    path('api/collections/context-data/', CollectionsContextAPI.as_view(), name='collections_context_api'),
    path('api/collections/', CollectionsCreateUpdateAPI.as_view(), name='collections_create_api'),
    path('api/collections/<int:collection_id>/', CollectionsCreateUpdateAPI.as_view(), name='collections_update_api'),
    path('api/collections/<int:collection_id>/delete/', CollectionsVoidAPI.as_view(), name='collections_delete_api'),
    path('api/collections/delete/', CollectionsVoidAPI.as_view(), name='collections_bulk_delete_api'),
    path('api/collections/<int:collection_id>/void/', CollectionsVoidAPI.as_view(), name='collections_void_api'),
    path('api/payments/', PaymentCreateUpdateAPI.as_view(), name='payments_create_api'),
    path('api/payments/<int:payment_id>/delete/', PaymentVoidAPI.as_view(), name='payments_delete_api'),
    path('api/payments/delete/', PaymentVoidAPI.as_view(), name='payments_bulk_delete_api'),
    path('trade/payment/<int:pk>/', PaymentDetailView.as_view(), name='payment_detail'),
    # credit notes
    path('api/creditnote/invoices/', CreditNoteInvoicesAPI.as_view(), name='creditnote_invoices_api'),
    path('trade/credit-notes/', CreditNoteListView.as_view(), name='creditnote_list'),
    path('trade/credit-notes/nueva/', CreditNoteCreateView.as_view(), name='creditnote_create'),
    path('trade/credit-notes/<int:pk>/', CreditNoteDetailView.as_view(), name='creditnote_detail'),
    path('trade/credit-notes/<int:pk>/void/', CreditNoteVoidView.as_view(), name='creditnote_void'),
]
