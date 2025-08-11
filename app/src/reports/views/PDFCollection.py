from django.http import FileResponse
from django.views import View
from playwright.sync_api import sync_playwright
from django.urls import reverse
from common.AppLoger import loggin_event
from django.conf import settings


class PDFCollection(View):
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

    def get(self, request, id_collection, *args, **kwargs):
        """Genera un PDF del comprobante de cobro y lo devuelve como respuesta."""
        target_url = str(request.build_absolute_uri(
            reverse("collection_template", kwargs={"id_collection": id_collection})
        ))

        if settings.IS_IN_PRODUCTION:
            target_url = target_url.replace('http', 'https')

        loggin_event(f'Generando PDF del cobro {id_collection} {target_url}')
        
        # Ruta temporal para el archivo PDF
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            output_path = tmp_file.name
        
        try:
            self.render_and_capture_pdf(target_url, output_path)
            
            # Leer el archivo generado y devolverlo como respuesta
            response = FileResponse(
                open(output_path, 'rb'),
                content_type='application/pdf'
            )
            response['Content-Disposition'] = f'attachment; filename="cobro_{id_collection}.pdf"'
            
            return response
            
        except Exception as e:
            loggin_event(f'Error al generar el PDF del cobro {id_collection}: {str(e)}')
            raise
            
        finally:
            # Eliminar el archivo temporal si existe
            if os.path.exists(output_path):
                try:
                    os.unlink(output_path)
                except Exception as e:
                    loggin_event(f'Error al eliminar archivo temporal {output_path}: {str(e)}')