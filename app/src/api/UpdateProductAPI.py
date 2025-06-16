from products.models import Product
from django.views.generic import View
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Q
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
            new_colors = data.get('new_colors', '').strip() if data.get('new_colors') else None

            # Validaciones básicas
            if not isinstance(product_ids, list) or len(product_ids) == 0:
                return JsonResponse(
                    {'message': 'product_ids debe ser una lista no vacía',
                        'status': 'error'},
                    safe=False,
                    status=400
                )

            if not new_name:
                return JsonResponse(
                    {'message': 'El nuevo nombre no puede estar vacío',
                        'status': 'error'},
                    safe=False,
                    status=400
                )

            loggin_event(f'Actualizando {len(product_ids)} productos con nombre: {new_name}, colores: {new_colors}')

            # Verificar que los productos existan
            existing_products = Product.objects.filter(
                id__in=product_ids, is_active=True)
            existing_ids = list(existing_products.values_list('id', flat=True))

            if len(existing_ids) != len(product_ids):
                non_existing_ids = [pid for pid in product_ids if pid not in existing_ids]
                return JsonResponse(
                    {'message': f'Los siguientes productos no existen: {non_existing_ids}',
                        'status': 'error'},
                    safe=False,
                    status=404
                )

            # Validar unicidad de nombre + variedad
            conflicts = []
            for product in existing_products:
                # Verificar si ya existe otro producto con el mismo nombre y variedad
                # (excluyendo los productos que estamos actualizando)
                existing_combination = Product.objects.filter(
                    name=new_name,
                    variety=product.variety,
                    is_active=True
                ).exclude(id__in=product_ids).exists()

                if existing_combination:
                    conflicts.append(f"{new_name} - {product.variety}")

            if conflicts:
                return JsonResponse(
                    {'message': f'Ya existen productos con estas combinaciones nombre-variedad: {", ".join(set(conflicts))}',
                        'status': 'error'},
                    safe=False,
                    status=409
                )

            # Realizar la actualización en una transacción
            with transaction.atomic():
                update_fields = {'name': new_name}
                
                if new_colors is not None:
                    update_fields['colors'] = new_colors if new_colors else 'NO DEFINIDO'

                updated_count = existing_products.update(**update_fields)

                loggin_event(f'Se actualizaron {updated_count} productos exitosamente')

                # Obtener los productos actualizados para logging
                updated_products = Product.objects.filter(id__in=existing_ids)
                updated_info = [
                    f"ID {p.id}: {p.name} - {p.variety} (colores: {p.colors})"
                    for p in updated_products
                ]
                loggin_event(f'Productos actualizados: {"; ".join(updated_info)}')

                response_data = {
                    'message': f'Se actualizaron {updated_count} productos exitosamente',
                    'status': 'success',
                    'updated_count': updated_count,
                    'updated_fields': {
                        'name': new_name,
                        'colors': new_colors if new_colors is not None else 'Sin cambios'
                    }
                }

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
                {'message': f'Error interno del servidor: {str(e)}', 'status': 'error'},
                safe=False,
                status=500
            )
