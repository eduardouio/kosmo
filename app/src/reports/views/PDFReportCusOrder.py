from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from trade.models import Order
from common.AppLoger import loggin_event
from django.conf import settings


# http://localhost:8000/reports/order-customer/12/
class PDFReportCusOrder(View):
    def render_pdf_to_bytes(self, url):
        """Renderiza la página con Playwright y devuelve el PDF como bytes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            page.goto(url)

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(200)  # Tiempo extra para aplicar estilos
            
            # Generar el PDF en memoria
            pdf_bytes = page.pdf(
                format="A4",
                margin={
                    "top": "1cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "1cm"
                },
                print_background=True
            )
            browser.close()
            return pdf_bytes

    def get(self, request, id_order, *args, **kwargs):
        """Genera un PDF de la orden de venta y lo devuelve como respuesta."""
        target_url = str(request.build_absolute_uri(
            reverse("order_customer_template", kwargs={"id_order": id_order})
        ))

        if settings.IS_IN_PRODUCTION:
            target_url = target_url.replace('http', 'https')

        loggin_event(f'Generando PDF de la orden de venta {id_order} {target_url}')
        order = Order.objects.get(id=id_order)
        pdf_bytes = self.render_pdf_to_bytes(target_url)
        
        # Crear respuesta con el PDF en memoria
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="OrdVenta-{order.partner} {order.serie}-{order.consecutive:06d}.pdf"'
        return response
