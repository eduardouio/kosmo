from django.http import HttpResponse, Http404
import os
from django.conf import settings


def pki_validation_view(request, filename):
    # Construir la ruta al archivo
    static_dir = settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else settings.STATIC_ROOT
    file_path = os.path.join(static_dir, '.well-known', 'pki-validation', filename)
    
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return HttpResponse(content, content_type='text/plain')
    except FileNotFoundError:
        raise Http404("Archivo de validación no encontrado")
