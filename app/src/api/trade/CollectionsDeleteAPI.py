
import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.core.exceptions import ValidationError

from trade.models import Payment, PaymentDetail
from common.AppLoger import loggin_event


class CollectionsDeleteAPI(View):

    def delete(self, request, collection_id):
        """Eliminar (soft delete) un cobro específico"""
        loggin_event(f'Eliminando cobro ID: {collection_id}')

        try:
            # Buscar el cobro (Payment con type_transaction='INGRESO')
            collection = Payment.objects.get(
                id=collection_id,
                type_transaction='INGRESO',
                is_active=True
            )
        except Payment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cobro no encontrado'
            }, status=404)

        try:
            with transaction.atomic():
                # Verificar si el cobro está en estado que permita eliminación
                if collection.status == 'CONFIRMADO':
                    return JsonResponse({
                        'success': False,
                        'error': 'No se puede eliminar un cobro confirmado'
                    }, status=400)

                # Soft delete del cobro
                collection.is_active = False
                collection.save()

                # Soft delete de los detalles asociados
                PaymentDetail.objects.filter(
                    payment=collection
                ).update(is_active=False)

                loggin_event(
                    f'Cobro {collection.payment_number} eliminado exitosamente')

                return JsonResponse({
                    'success': True,
                    'message': f'Cobro {collection.payment_number} eliminado exitosamente'
                })

        except Exception as e:
            loggin_event(f'Error al eliminar cobro: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)

    def post(self, request):
        """Eliminar (soft delete) múltiples cobros"""
        loggin_event('Eliminando múltiples cobros')

        try:
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)

            data = json.loads(request.body)

            if 'collection_ids' not in data or not data['collection_ids']:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe proporcionar al menos un ID de cobro'
                }, status=400)

            collection_ids = data['collection_ids']
            deleted_collections = []
            errors = []

            with transaction.atomic():
                for collection_id in collection_ids:
                    try:
                        # Buscar el cobro
                        collection = Payment.objects.get(
                            id=collection_id,
                            type_transaction='INGRESO',
                            is_active=True
                        )

                        # Verificar si el cobro está en estado que permita eliminación
                        if collection.status == 'CONFIRMADO':
                            errors.append({
                                'collection_id': collection_id,
                                'error': f'Cobro {collection.payment_number} está confirmado y no se puede eliminar'
                            })
                            continue

                        # Soft delete del cobro
                        collection.is_active = False
                        collection.save()

                        # Soft delete de los detalles asociados
                        PaymentDetail.objects.filter(
                            payment=collection
                        ).update(is_active=False)

                        deleted_collections.append({
                            'collection_id': collection_id,
                            'payment_number': collection.payment_number
                        })

                        loggin_event(
                            f'Cobro {collection.payment_number} eliminado en lote')

                    except Payment.DoesNotExist:
                        errors.append({
                            'collection_id': collection_id,
                            'error': 'Cobro no encontrado'
                        })
                    except Exception as e:
                        errors.append({
                            'collection_id': collection_id,
                            'error': str(e)
                        })

                return JsonResponse({
                    'success': True,
                    'message': f'Proceso de eliminación completado',
                    'deleted_collections': deleted_collections,
                    'errors': errors,
                    'summary': {
                        'total_requested': len(collection_ids),
                        'successfully_deleted': len(deleted_collections),
                        'errors_count': len(errors)
                    }
                })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            loggin_event(f'Error en eliminación múltiple de cobros: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
