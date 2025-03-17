from django.http import FileResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from trade.models import Order
from common.AppLoger import loggin_event


class PDFReportSupOrder(View):
    def render_and_capture_pdf(self, url, output_path):
        """Renderiza la página con Playwright y la guarda como PDF."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)
            page.goto(url)

            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(200)  # Tiempo extra para aplicar estilos
            page.pdf(
                path=output_path,
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

    def get(self, request, id_order, *args, **kwargs):
        """Genera un PDF de la página y lo devuelve como respuesta."""
        target_url = str(request.build_absolute_uri(
            reverse("order_supplier_template", kwargs={"id_order": id_order})
        ))

        target_url = target_url.replace('http', 'https')

        loggin_event(f'Generando PDF de la orden {id_order} {target_url}')
        order = Order.objects.get(id=id_order)
        output_pdf = f"PO-{id_order}-{order.partner.short_name}.pdf"
        self.render_and_capture_pdf(target_url, output_pdf)

        return FileResponse(
            open(output_pdf, "rb"),
            content_type="application/pdf",
            as_attachment=True
        )

