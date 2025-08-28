"""
Middleware personalizado para registrar accesos a enlaces de la aplicación
"""
import time
from django.utils.deprecation import MiddlewareMixin
from common.AppLoger import log_access, log_access_error


class AccessLoggerMiddleware(MiddlewareMixin):
    """
    Middleware que registra todos los accesos a los enlaces de la aplicación
    incluyendo información del usuario cuando esté disponible
    """
    
    def process_request(self, request):
        """
        Procesa la petición antes de que llegue a la vista
        """
        # Guardamos el tiempo de inicio para calcular la duración
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Procesa la respuesta después de que se ejecute la vista
        """
        try:
            # Información básica de la petición
            method = request.method
            path = request.get_full_path()
            status_code = response.status_code
            
            # Información del usuario
            user_info = "Usuario: Anónimo"
            if hasattr(request, 'user') and request.user.is_authenticated:
                if (hasattr(request.user, 'get_full_name') and
                        request.user.get_full_name()):
                    user_info = f"Usuario: {request.user.get_full_name()}"
                elif (hasattr(request.user, 'username') and
                        request.user.username):
                    user_info = f"Usuario: {request.user.username}"
                else:
                    user_info = f"Usuario: {request.user.id}"
            
            # Información de IP y User-Agent
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get(
                'HTTP_USER_AGENT', 'No disponible'
            )[:100]  # Limitamos el user agent
            
            # Calcular tiempo de respuesta
            duration = ""
            if hasattr(request, '_start_time'):
                duration_ms = (time.time() - request._start_time) * 1000
                duration = f" | Duración: {duration_ms:.2f}ms"
            
            # Filtrar solo peticiones importantes (no assets estáticos)
            if self._should_log_request(path):
                log_message = (
                    f"ACCESO: {method} {path} | "
                    f"Estado: {status_code} | "
                    f"{user_info} | "
                    f"IP: {ip_address} | "
                    f"User-Agent: {user_agent}"
                    f"{duration}"
                )
                
                # Registrar acceso
                is_error = status_code >= 400
                if is_error:
                    log_access_error(log_message)
                else:
                    log_access(log_message)
        
        except Exception as e:
            # Si hay error en el logging, lo registramos pero no
            # interrumpimos la respuesta
            log_access_error(f"Error en AccessLoggerMiddleware: {str(e)}")
        
        return response
    
    def _get_client_ip(self, request):
        """
        Obtiene la IP real del cliente considerando proxies
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'IP no disponible')
        return ip
    
    def _should_log_request(self, path):
        """
        Determina si una petición debe ser registrada.
        Excluye archivos estáticos y otros recursos no importantes
        """
        # Excluir archivos estáticos comunes
        static_extensions = [
            '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico',
            '.svg', '.woff', '.woff2', '.ttf', '.eot', '.map'
        ]
        
        # Excluir rutas estáticas
        static_paths = [
            '/static/', '/media/', '/favicon.ico', '/robots.txt'
        ]
        
        # Verificar extensiones
        for ext in static_extensions:
            if path.lower().endswith(ext):
                return False
        
        # Verificar rutas estáticas
        for static_path in static_paths:
            if path.startswith(static_path):
                return False
        
        # Excluir peticiones AJAX de heartbeat o polling si existen
        if 'heartbeat' in path.lower() or 'ping' in path.lower():
            return False
            
        return True
