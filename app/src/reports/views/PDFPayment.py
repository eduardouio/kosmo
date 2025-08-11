from django.http import FileResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from trade.models import Payment
from common.AppLoger import loggin_event
from django.conf import settings


class PDFPayment(View):
    def render_and_capture_pdf(self, url, output_path):
        """Renderiza la página con Playwright y la guarda como PDF."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            
            # Configurar la vista para que se ajuste al 80%
            page.set_viewport_size({"width": 1240, "height": 1754})  # Tamaño A4 en píxeles (1.4 * 72 DPI)
            
            # Aplicar zoom al 80%
            page.set_viewport_size({"width": int(1240 * 0.8), "height": int(1754 * 0.9)})
            
            page.goto(url)
            page.wait_for_load_state("networkidle")
            
            # Generar el PDF con la escala al 80%
            page.pdf(
                path=output_path,
                format="A4",
                margin={
                    "top": "1cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "1cm"
                },
                print_background=True,
                scale=0.8  # Aplicar escala del 80%
            )
            browser.close()

    def get(self, request, id_payment, *args, **kwargs):
        """Genera un PDF del comprobante de pago y lo devuelve como respuesta."""
        target_url = str(request.build_absolute_uri(
            reverse("payment_template", kwargs={"id_payment": id_payment})
        ))

        if settings.IS_IN_PRODUCTION:
            target_url = target_url.replace('http', 'https')

        loggin_event(f'Generando PDF del pago {id_payment} {target_url}')
        payment = Payment.objects.get(id=id_payment)
        output_pdf = f"Payment-{id_payment}-{payment.payment_number or 'no-number'}.pdf"
        self.render_and_capture_pdf(target_url, output_pdf)

        return FileResponse(
            open(output_pdf, "rb"),
            content_type="application/pdf",
            as_attachment=True,
            filename=output_pdf
        )