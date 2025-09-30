from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from trade.models import CreditNote
from common.AppLoger import loggin_event
from django.conf import settings


class PDFCreditNote(View):
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

    def get(self, request, id_credit_note, *args, **kwargs):
        """Genera un PDF de la nota de crédito y lo devuelve como respuesta."""
        # Usar BASE_URL de settings para evitar problemas con localhost
        creditnote_path = reverse(
            "creditnote_template", kwargs={"id_credit_note": id_credit_note}
        )
        target_url = f"{settings.BASE_URL}{creditnote_path}"

        loggin_event(
            f'Generando PDF de la nota de crédito '
            f'{id_credit_note} {target_url}'
        )
        credit_note = CreditNote.objects.get(id=id_credit_note)
        pdf_bytes = self.render_pdf_to_bytes(target_url)
        
        # Crear respuesta con el PDF en memoria
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        filename = (
            f'NotaCredito-{credit_note.invoice.partner} '
            f'{credit_note.num_credit_note}.pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
