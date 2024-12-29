const idStockDay = 1;
const apiBaseUrl = 'http://localhost:8000';
const csrfToken = 'aqui_va_el_csrf_token';

export const appConfig = {
    "apiBaseUrl": apiBaseUrl,
    "csrfToken": csrfToken,
    "idStock": idStockDay,
    "urlLogo": apiBaseUrl + "/static/img/logo-kosmo.png",
    "urlDispo": apiBaseUrl + "/api/stock_detail/" + idStockDay + "/",
    "urlAnalyce": apiBaseUrl + "/api/analize_stock_text/",
    "urlAllSuppliers": apiBaseUrl + "/api/partners/all-supliers/",
    "headers": {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    }
}
