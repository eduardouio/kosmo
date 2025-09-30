from django.http import HttpResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from partners.models import Partner
from common.AppLoger import loggin_event
from django.conf import settings


class PDFBalance(View):
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

    def get(self, request, partner_id, *args, **kwargs):
        """Genera un PDF del estado de cuenta y lo devuelve como respuesta."""
        # Usar BASE_URL de settings para evitar problemas con localhost
        balance_path = reverse(
            "balance_template", kwargs={"partner_id": partner_id}
        )
        target_url = f"{settings.BASE_URL}{balance_path}"
        
        # Agregar parámetros GET si existen (fechas de inicio y fin)
        query_params = []
        if request.GET.get('start_date'):
            query_params.append(f"start_date={request.GET.get('start_date')}")
        if request.GET.get('end_date'):
            query_params.append(f"end_date={request.GET.get('end_date')}")
        
        if query_params:
            target_url += "?" + "&".join(query_params)

        loggin_event(
            f'Generando PDF del estado de cuenta del partner {partner_id} '
            f'{target_url}'
        )
        
        try:
            partner = Partner.objects.get(id=partner_id)
        except Partner.DoesNotExist:
            loggin_event(
                f'Partner con ID {partner_id} no encontrado', error=True
            )
            return HttpResponse('Partner no encontrado', status=404)
        
        pdf_bytes = self.render_pdf_to_bytes(target_url)
        
        # Crear respuesta con el PDF en memoria
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        
        # Generar nombre del archivo con fechas si están disponibles
        filename_parts = [f"Estado-Cuenta-{partner.name}"]
        if request.GET.get('start_date'):
            filename_parts.append(f"desde-{request.GET.get('start_date')}")
        if request.GET.get('end_date'):
            filename_parts.append(f"hasta-{request.GET.get('end_date')}")
        
        filename = "_".join(filename_parts) + ".pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
