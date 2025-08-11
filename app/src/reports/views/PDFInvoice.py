from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from trade.models import Invoice
from common.AppLoger import loggin_event
from django.conf import settings


class PDFInvoice(View):
    def render_pdf_to_bytes(self, url):
        """Renderiza la página con Playwright y devuelve el PDF como bytes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            page.goto(url)

            page.wait_for_load_state("networkidle")
            
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

    def get(self, request, id_invoice, *args, **kwargs):
        """Genera un PDF de la factura y lo devuelve como respuesta."""
        target_url = str(request.build_absolute_uri(
            reverse("invoice_template", kwargs={"id_invoice": id_invoice})
        ))

        if settings.IS_IN_PRODUCTION:
            target_url = target_url.replace('http', 'https')

        loggin_event(f'Generando PDF de la factura {id_invoice} {target_url}')
        invoice = Invoice.objects.get(id=id_invoice)
        pdf_bytes = self.render_pdf_to_bytes(target_url)
        
        # Crear respuesta con el PDF en memoria
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Factura-{invoice.partner} {invoice.serie}-{invoice.consecutive:06d}.pdf"'
        return response
