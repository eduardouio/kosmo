from django.http import JsonResponse
from django.views import View
from django.conf import settings
from common.AppLoger import loggin_event


class BankConfigAPI(View):
    """API para obtener la configuración bancaria por defecto"""

    def get(self, request):
        """Obtener la configuración bancaria para pagos"""
        loggin_event('Obteniendo configuración bancaria')
        
        try:
            bank_config = settings.BANK_ACCOUNT
            
            # Formatear la respuesta para el frontend
            response_data = {
                'bank_name': bank_config.get('bank_name', ''),
                'account_number': bank_config.get('account_number', ''),
                'account_type': bank_config.get('account_type', ''),
                'account_holder': bank_config.get('account_holder', ''),
                'bank_address': bank_config.get('bank_address', ''),
                'bank_phone': bank_config.get('bank_phone', ''),
                'bank_email': bank_config.get('bank_email', '')
            }
            
            return JsonResponse({
                'success': True,
                'data': response_data
            }, status=200)
            
        except Exception as e:
            loggin_event(f'Error obteniendo configuración bancaria: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': 'Error obteniendo configuración bancaria'
            }, status=500)
