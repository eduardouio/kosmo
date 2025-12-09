from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from common.AppLoger import loggin_event
from django.conf import settings
from trade.models import Payment


class PDFCollection(View):
    def render_pdf_to_bytes(self, url):
        """Renderiza la página con Playwright y devuelve el PDF como bytes."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(ignore_https_errors=True)

            page.set_viewport_size({"width": 1240, "height": 1754})

            page.set_viewport_size(
                {"width": int(1240 * 0.8), "height": int(1754 * 0.9)}
            )

            page.goto(url)
            page.wait_for_load_state("networkidle")

            pdf_bytes = page.pdf(
                format="A4",
                margin={
                    "top": "1cm",
                    "right": "0.5cm",
                    "bottom": "0.5cm",
                    "left": "1cm",
                },
                print_background=True,
                scale=0.8,
            )
            browser.close()
            return pdf_bytes

    def get(self, request, id_collection, *args, **kwargs):
        """Genera un PDF del comprobante de cobro y lo devuelve como respuesta."""

        collection_path = reverse(
            "collection_template", kwargs={"id_collection": id_collection}
        )
        target_url = f"{settings.BASE_URL}{collection_path}"

        loggin_event(f"Generando PDF del pago {id_collection} {target_url}")
        payment = Payment.objects.get(id=id_collection)

        payment_detail = payment.invoices.first()
        client_name = "Cliente-Desconocido"
        invoice_number = "SIN-FACTURA"

        if (
            payment_detail
            and hasattr(payment_detail, "invoice")
            and payment_detail.invoice
        ):
            if (
                hasattr(payment_detail.invoice, "partner")
                and payment_detail.invoice.partner
            ):
                client_name = payment_detail.invoice.partner.name.replace(" ", "-")
            if (
                hasattr(payment_detail.invoice, "num_invoice")
                and payment_detail.invoice.num_invoice
            ):
                invoice_number = payment_detail.invoice.num_invoice.replace(" ", "")

        pdf_bytes = self.render_pdf_to_bytes(target_url)

        safe_client_name = "".join(
            [c for c in client_name if c.isalpha() or c.isdigit() or c in ("-", "_")]
        ).rstrip()
        safe_invoice = "".join(
            [c for c in invoice_number if c.isalpha() or c.isdigit() or c in ("-", "_")]
        ).rstrip()

        filename = f"Cobro-{payment.payment_number or payment.id}-{safe_client_name}-{safe_invoice}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
