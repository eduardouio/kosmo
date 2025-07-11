const idStockDay = window.djangoConfig?.stockId ?? 1;
const apiBaseUrl = window.djangoConfig?.baseUrl ?? "http://localhost:8000";
const apiBaseUrlTest = apiBaseUrl;
const csrfToken = window.djangoConfig?.csrfToken ?? "";


export const appConfig = {
    "apiBaseUrl": apiBaseUrl,
    "apiBaseUrlTest": apiBaseUrlTest,
    "csrfToken": csrfToken,
    "idStock": idStockDay,
    "imgPlaceholder": apiBaseUrl + "/static/img/rosa_placeholder.jpg",
    "urlLogo": apiBaseUrl + "/static/img/logo-kosmo.png",
    "urlDispo": apiBaseUrl + `/api/stock_detail/${idStockDay}/`,
    "urlAnalyce": apiBaseUrl + "/api/analize_stock_text/",
    "urlAllSuppliers": apiBaseUrl + `/api/partners/all-supliers/?id_stock=${idStockDay}`,
    "urlAllCustomers": apiBaseUrl + "/api/partners/all-customers/",
    "urlDeleteStockDetail": apiBaseUrl + "/api/delete_stock_detail/",
    "urlUpdateStockDetail": apiBaseUrl + "/api/update_stock_detail/",
    "urlAllProducts": apiBaseUrl + "/api/products/all_products/",
    "urlAddBoxItem": apiBaseUrl + "/api/stock/add_box_item/",
    "urlCreateOrder": apiBaseUrl + "/api/orders/create-customer-order/",
    "urlCreateFutureOrder": apiBaseUrl + "/api/orders/create-future-order/",
    "urlOrdersByStock": apiBaseUrl + `/api/orders/by_stock_day/${idStockDay}/`,
    "urlUpdateOrder": apiBaseUrl + "/api/orders/update-customer-order/",
    "urlPurchaseOrdersByCustomerOrder": apiBaseUrl + "/api/orders/purchase_orders/{id_customer_order}/",
    "urlUpdateSupplierOrder": apiBaseUrl + "/api/orders/update-supplier-order/",
    "urlCancelOrder": apiBaseUrl + "/api/orders/cancel-order/",
    "urlCancelSupplierOrder": apiBaseUrl + "/api/orders/cancel-supplier-order/",
    "urlConfirmOrder": apiBaseUrl + "/api/orders/confirm-order/",
    "urlReportSupOrder": apiBaseUrl + "/reports/order-supplier/{id_order}/",
    "urlReportCustOrder": apiBaseUrl + "/reports/order-customer/{id_order}/",
    "urlCreateInvoiceOrder": apiBaseUrl + "/api/invoice/create-by-order/",
    "urlInvoiceReport": apiBaseUrl + "/reports/invoice/{id_invoice}/",
    "urlOrderCustomerDetail": apiBaseUrl + "/api/orders/customer-order-detail/{id_customer_order}/",
    "urlUpdateCustomerOrder": apiBaseUrl + "/api/orders/update-future-order/",
    "headers": {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken
    }
}
