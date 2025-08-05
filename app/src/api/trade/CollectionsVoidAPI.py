
import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction

from trade.models import Payment
from common.AppLoger import loggin_event
from common.InvoiceBalance import InvoiceBalance


class CollectionsVoidAPI(View):

    def delete(self, request, collection_id):
        """Anular un cobro específico por ID en la URL"""
        loggin_event(f'Anulando cobro {collection_id}')

        try:
            collection = Payment.objects.get(
                id=collection_id,
                type_transaction='INGRESO'
            )
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Collection not found'}, status=404)

        # Verificar que el cobro se pueda anular
        if collection.status == 'ANULADO':
            return JsonResponse(
                {'error': 'Collection is already voided'},
                status=400
            )

        try:
            with transaction.atomic():
                # Revertir los saldos de las facturas antes de anular
                revert_success = InvoiceBalance.revert_payment_from_invoices(
                    collection_id
                )

                if not revert_success:
                    return JsonResponse(
                        {
                            'error': 'Failed to revert invoice balances'
                        },
                        status=500
                    )

                # Cambiar estado del cobro a ANULADO
                collection.status = 'ANULADO'
                collection.save()

                loggin_event(f'Cobro anulado: {collection.payment_number}')

                return JsonResponse({
                    'message': 'Collection voided successfully',
                    'collection_id': collection.id,
                    'payment_number': collection.payment_number
                }, status=200)

        except Exception as e:
            loggin_event(
                f'Error inesperado al anular cobro: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)

    def post(self, request):
        """Anular cobros cambiando estado a ANULADO y revirtiendo saldos"""
        loggin_event('Anulando cobros')

        try:
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)
            collection_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not collection_data:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Validar que se proporcione una lista de IDs de cobros
        if 'collection_ids' not in collection_data:
            return JsonResponse(
                {'error': 'collection_ids field is required'},
                status=400
            )

        collection_ids = collection_data['collection_ids']
        if not isinstance(collection_ids, list) or len(collection_ids) == 0:
            return JsonResponse(
                {'error': 'collection_ids must be a non-empty list'},
                status=400
            )

        voided_collections = []
        not_found_collections = []
        cannot_void_collections = []

        try:
            with transaction.atomic():
                for collection_id in collection_ids:
                    try:
                        collection = Payment.objects.get(
                            id=collection_id,
                            type_transaction='INGRESO'
                        )

                        # Verificar que el cobro se pueda anular
                        # No se pueden anular cobros ya anulados
                        if collection.status == 'ANULADO':
                            cannot_void_collections.append({
                                'id': collection_id,
                                'payment_number': collection.payment_number,
                                'reason': 'Collection is already voided'
                            })
                            continue

                        # Revertir los saldos de las facturas antes de anular
                        revert_success = (
                            InvoiceBalance.revert_payment_from_invoices(
                                collection_id
                            )
                        )
                        
                        if not revert_success:
                            cannot_void_collections.append({
                                'id': collection_id,
                                'payment_number': collection.payment_number,
                                'reason': 'Failed to revert invoice balances'
                            })
                            continue

                        # Cambiar estado del cobro a ANULADO
                        collection.status = 'ANULADO'
                        collection.save()

                        voided_collections.append({
                            'id': collection.id,
                            'payment_number': collection.payment_number
                        })

                        loggin_event(
                            f'Cobro anulado: {collection.payment_number}')

                    except Payment.DoesNotExist:
                        not_found_collections.append(collection_id)
                        continue

                # Preparar respuesta
                response_data = {
                    'message': (f'{len(voided_collections)} collections voided '
                                'successfully')
                }

                if voided_collections:
                    response_data['voided_collections'] = voided_collections

                if not_found_collections:
                    response_data['not_found_collections'] = not_found_collections

                if cannot_void_collections:
                    response_data['cannot_void_collections'] = (
                        cannot_void_collections
                    )

                # Determinar código de estado
                if len(voided_collections) == len(collection_ids):
                    status_code = 200  # Todo se anuló correctamente
                elif len(voided_collections) > 0:
                    status_code = 207  # Anulación parcial
                else:
                    status_code = 400  # No se pudo anular ninguno

                return JsonResponse(response_data, status=status_code)

        except Exception as e:
            loggin_event(
                f'Error inesperado al anular cobros: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)
