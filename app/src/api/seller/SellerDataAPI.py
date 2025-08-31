from django.views.generic import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from common.SellerData import SellerData
import json


@method_decorator(csrf_exempt, name='dispatch')
class SellerDataAPI(View):
    """
    API para obtener información detallada de vendedores.

    Endpoints:
        GET: Obtiene información de un vendedor específico o todos los vendedores

    Query Parameters:
        user_id: ID del vendedor específico (opcional)
        summary: Si es 'true', retorna resumen de todos los vendedores
    """

    def get(self, request, *args, **kwargs):
        """
        Maneja peticiones GET para obtener información de vendedores.

        Returns:
            JsonResponse con la información del vendedor o vendedores
        """
        try:
            # Obtener parámetros de la query
            user_id = request.GET.get('user_id')
            summary = request.GET.get('summary', 'false').lower() == 'true'

            # Si se solicita resumen de todos los vendedores
            if summary:
                sellers_summary = SellerData.get_all_sellers_summary()
                return JsonResponse({
                    'success': True,
                    'data': sellers_summary,
                    'count': len(sellers_summary)
                }, status=200)

            # Si se especifica un user_id
            if user_id:
                try:
                    user_id = int(user_id)
                    seller_info = SellerData.get_seller_info(user_id)

                    # Verificar si hubo error
                    if 'error' in seller_info:
                        return JsonResponse({
                            'success': False,
                            'error': seller_info['error']
                        }, status=404)

                    return JsonResponse({
                        'success': True,
                        'data': seller_info
                    }, status=200)

                except ValueError:
                    return JsonResponse({
                        'success': False,
                        'error': 'El user_id debe ser un número entero válido'
                    }, status=400)

            # Si no se especifica ningún parámetro, retornar error
            return JsonResponse({
                'success': False,
                'error': 'Debe especificar user_id o summary=true'
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)

    def post(self, request, *args, **kwargs):
        """
        Maneja peticiones POST para obtener información de múltiples vendedores.

        Body:
            user_ids: Lista de IDs de vendedores

        Returns:
            JsonResponse con la información de los vendedores solicitados
        """
        try:
            # Parsear el body de la petición
            data = json.loads(request.body)
            user_ids = data.get('user_ids', [])

            if not user_ids:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe proporcionar una lista de user_ids'
                }, status=400)

            # Obtener información de cada vendedor
            sellers_data = []
            errors = []

            for user_id in user_ids:
                try:
                    seller_info = SellerData.get_seller_info(int(user_id))

                    if 'error' in seller_info:
                        errors.append({
                            'user_id': user_id,
                            'error': seller_info['error']
                        })
                    else:
                        sellers_data.append(seller_info)

                except (ValueError, TypeError):
                    errors.append({
                        'user_id': user_id,
                        'error': 'ID de usuario inválido'
                    })

            return JsonResponse({
                'success': True,
                'data': sellers_data,
                'errors': errors if errors else None,
                'count': len(sellers_data)
            }, status=200)

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'El body debe ser un JSON válido'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
