from django.urls import path
from api import (
    AnalizeStockTextAPI,
    StockDetailAPI,
    AllSuppliersAPI,
    DeleteStockDetailAPI,
    UpdateStockDetailAPI,
    AllProductsAPI,
    AddBoxItemAPI,
    AllCustomerAPI,
    CreateOrderAPI,
    UpdateCustmerOrderAPI,
    OrderPurchaseByOrderSale,
    AllOrderDetailAPI,
    UpdateSupplierOrderAPI,
    CancelCustomerOrderAPI,
    CancelSupplierOrderAPI,
    AprovePurchaseOrderAPI,
    CreateInvoiceAPI,
    CreateFutureOrderAPI,
    OrderDetailAPI,
    CustomerOrderDetailAPI,
    UpdateFutureOrderAPI,
    SellersListAPI,
    InvoicesForPaymentAPI,
    UpdateProductAPI,
    PaymentContextData,
    CollectionsContextAPI,
    CustomerInvoiceDetailAPI,
    InvoicesByPartnerAPI,
)
from api.trade import (
    PaymentCreateUpdateAPI,
    PaymentVoidAPI,
    CollectionsCreateUpdateAPI,
    CollectionsVoidAPI,
    BankConfigAPI,
    CollectionsContextAPI,
)

from api.seller import (
    SellerDataAPI
)

from api.users import UpdateUserAPIView

urlpatterns = [
    path('api/stock_detail/<int:stock_day_id>/', StockDetailAPI.as_view(), name='stock_detail'),
    path('api/partners/all-supliers/', AllSuppliersAPI.as_view(), name='all_supliers'),
    path('api/partners/all-customers/', AllCustomerAPI.as_view(), name='all_customers'),
    path('api/analize_stock_text/', AnalizeStockTextAPI.as_view(), name='analize_stock_text'),
    path('api/delete_stock_detail/', DeleteStockDetailAPI.as_view(), name='delete_stock_detail'),
    path('api/update_stock_detail/', UpdateStockDetailAPI.as_view(), name='update_stock_detail'),
    path('api/products/all_products/', AllProductsAPI.as_view(), name='all_products'),
    path('api/stock/add_box_item/', AddBoxItemAPI.as_view(), name='add_box_item'),
    path('api/orders/by_stock_day/<int:id_stock_day>/', AllOrderDetailAPI.as_view(), name='order_detail_by_stock_day'),
    path('api/orders/purchase_orders/<int:order_customer_id>/', OrderPurchaseByOrderSale.as_view(), name='purchase_by_order_sale'),
    path('api/orders/create-customer-order/', CreateOrderAPI.as_view(), name='create_order'),
    path('api/orders/create-future-order/', CreateFutureOrderAPI.as_view(), name='create_future_order'),
    path('api/orders/update-customer-order/', UpdateCustmerOrderAPI.as_view(), name='update_order'),
    path('api/orders/order-detail/<int:id_stock_day>/', AllOrderDetailAPI.as_view(), name='order_detail'),
    path('api/orders/update-supplier-order/', UpdateSupplierOrderAPI.as_view(), name='update_supplier_order'),
    path('api/orders/cancel-order/', CancelCustomerOrderAPI.as_view(), name='cancel_order'),
    path('api/orders/cancel-supplier-order/', CancelSupplierOrderAPI.as_view(), name='cancel_supplier_order'),
    path('api/orders/confirm-order/', AprovePurchaseOrderAPI.as_view(), name='confirm_purchase_order'),
    path('api/orders/approve-purchase-order/<int:order_id>/', AprovePurchaseOrderAPI.as_view(), name='approve_purchase_order_view'),
    path('api/orders/detail/<int:order_id>/', OrderDetailAPI.as_view(), name='order_detail'),
    path('api/invoice/create-by-order/', CreateInvoiceAPI.as_view(), name='create_invoice_by_order'),
    path('api/invoice/customer-invoice-detail/<int:invoice_id>/', CustomerInvoiceDetailAPI.as_view(), name='customer-invoice-detail'),
    path('api/orders/customer-order-detail/<int:order_id>/', CustomerOrderDetailAPI.as_view(), name='customer-order-detail'),
    path('api/orders/update-future-order/', UpdateFutureOrderAPI.as_view(), name='update_future_order'),
    path('api/documents-for-payment/', InvoicesForPaymentAPI.as_view(), name='documents_for_payment'),
    path('api/users/sellers/', SellersListAPI.as_view(), name='sellers_list_api'),
    path('api/products/bulk-update/', UpdateProductAPI.as_view(), name='update_product_api'),
    path('api/payments/context-data/', PaymentContextData.as_view(), name='payment_context_data'),
    path('api/collections/context-data/', CollectionsContextAPI.as_view(), name='collections_context_data'),
    path('api/bank-config/', BankConfigAPI.as_view(), name='bank_config'),
    # Payment APIs
    path('api/payments/', PaymentCreateUpdateAPI.as_view(), name='payment_create_list'),
    path('api/payments/<int:payment_id>/', PaymentCreateUpdateAPI.as_view(), name='payment_detail_update'),
    path('api/payments/delete/', PaymentVoidAPI.as_view(), name='payment_delete_bulk'),
    path('api/payments/<int:payment_id>/delete/', PaymentVoidAPI.as_view(), name='payment_delete'),

    # Collection APIs
    path('api/collections/', CollectionsCreateUpdateAPI.as_view(), name='collection_create_list'),
    path('api/collections/<int:collection_id>/', CollectionsCreateUpdateAPI.as_view(), name='collection_detail_update'),
    path('api/collections/delete/', CollectionsVoidAPI.as_view(), name='collection_delete_bulk'),
    path('api/collections/<int:collection_id>/delete/', CollectionsVoidAPI.as_view(), name='collection_delete'),
    path('api/collections-context/', CollectionsContextAPI.as_view(), name='collections_context_data'),
    # User APIs
    path('api/users/update/', UpdateUserAPIView.as_view(), name='update_user'),

    # Seller APIs
    path('api/sellers/data/', SellerDataAPI.as_view(), name='seller_data'),
    
    # Credit Note APIs
    path('api/invoices/by-partner/', InvoicesByPartnerAPI.as_view(), name='invoices_by_partner'),
]
