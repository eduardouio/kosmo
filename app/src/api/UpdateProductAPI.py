from products.models import Product
from django.views.generic import View
from django.http import JsonResponse
from common.AppLoger import loggin_event
import json


class UpdateProductAPI(View):
    def put(self, request, *args, **kwargs):
        try:
            loggin_event('UpdateProductAPI PUT request')
            data = json.loads(request.body)

            # Validar que vengan los campos requeridos
            if 'product_ids' not in data or 'new_name' not in data:
                return JsonResponse(
                    {'message': 'Faltan campos requeridos: product_ids y new_name',
                        'status': 'error'},
                    safe=False,
                    status=400
                )

            product_ids = data['product_ids']
            new_name = data['new_name'].strip()

            # Validar que product_ids sea una lista
            if not isinstance(product_ids, list) or len(product_ids) == 0:
                return JsonResponse(
                    {'message': 'product_ids debe ser una lista no vacía',
                        'status': 'error'},
                    safe=False,
                    status=400
                )

            # Validar que new_name no esté vacío
            if not new_name:
                return JsonResponse(
                    {'message': 'El nuevo nombre no puede estar vacío',
                        'status': 'error'},
                    safe=False,
                    status=400
                )

            loggin_event(
                f'Actualizando {len(product_ids)} productos con nombre: {new_name}')

            # Buscar productos que existen
            existing_products = Product.objects.filter(
                id__in=product_ids, is_active=True)
            existing_ids = list(existing_products.values_list('id', flat=True))

            # Identificar IDs que no existen
            non_existing_ids = [
                pid for pid in product_ids if pid not in existing_ids]

            if non_existing_ids:
                loggin_event(f'Productos no encontrados: {non_existing_ids}')

            # Actualizar productos existentes
            updated_count = existing_products.update(name=new_name)

            loggin_event(
                f'Se actualizaron {updated_count} productos exitosamente')

            response_data = {
                'message': f'Se actualizaron {updated_count} productos exitosamente',
                'status': 'success',
                'updated_count': updated_count,
                'total_requested': len(product_ids)
            }

            if non_existing_ids:
                response_data[
                    'warning'] = f'Los siguientes IDs no fueron encontrados: {non_existing_ids}'
                response_data['non_existing_ids'] = non_existing_ids

            return JsonResponse(response_data, safe=False, status=200)

        except json.JSONDecodeError:
            loggin_event('Error al decodificar JSON en UpdateProductAPI')
            return JsonResponse(
                {'message': 'JSON inválido', 'status': 'error'},
                safe=False,
                status=400
            )
        except Exception as e:
            loggin_event(f'Error en UpdateProductAPI: {str(e)}')
            return JsonResponse(
                {'message':
                    f'Error interno del servidor: {str(e)}', 'status': 'error'},
                safe=False,
                status=500
            )
