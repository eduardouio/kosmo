import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction

from trade.models import Payment, PaymentDetail
from common.AppLoger import loggin_event


class PaymentDeleteAPI(View):

    def post(self, request):
        """Eliminar pagos (soft delete desactivando is_active)"""
        loggin_event('Eliminando pagos')

        try:
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)
            payment_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not payment_data:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Validar que se proporcione una lista de IDs de pagos
        if 'payment_ids' not in payment_data:
            return JsonResponse(
                {'error': 'payment_ids field is required'},
                status=400
            )

        payment_ids = payment_data['payment_ids']
        if not isinstance(payment_ids, list) or len(payment_ids) == 0:
            return JsonResponse(
                {'error': 'payment_ids must be a non-empty list'},
                status=400
            )

        deleted_payments = []
        not_found_payments = []
        cannot_delete_payments = []

        try:
            with transaction.atomic():
                for payment_id in payment_ids:
                    try:
                        payment = Payment.objects.get(id=payment_id)

                        # Verificar que el pago se pueda eliminar
                        # No se pueden eliminar pagos confirmados o aprobados
                        if payment.status in ['CONFIRMADO', 'RECHAZADO']:
                            cannot_delete_payments.append({
                                'id': payment_id,
                                'payment_number': payment.payment_number,
                                'reason': f'Cannot delete payment with status: {payment.status}'
                            })
                            continue

                        # Realizar soft delete
                        payment.is_active = False
                        payment.save()

                        # También desactivar los detalles de pago asociados
                        PaymentDetail.objects.filter(payment=payment).update(
                            is_active=False
                        )

                        deleted_payments.append({
                            'id': payment.id,
                            'payment_number': payment.payment_number
                        })

                        loggin_event(
                            f'Pago eliminado: {payment.payment_number}')

                    except Payment.DoesNotExist:
                        not_found_payments.append(payment_id)
                        continue

                # Preparar respuesta
                response_data = {
                    'message': f'{len(deleted_payments)} payments deleted successfully'
                }

                if deleted_payments:
                    response_data['deleted_payments'] = deleted_payments

                if not_found_payments:
                    response_data['not_found_payments'] = not_found_payments

                if cannot_delete_payments:
                    response_data['cannot_delete_payments'] = cannot_delete_payments

                # Determinar código de estado
                if len(deleted_payments) == len(payment_ids):
                    status_code = 200  # Todo se eliminó correctamente
                elif len(deleted_payments) > 0:
                    status_code = 207  # Eliminación parcial
                else:
                    status_code = 400  # No se pudo eliminar ninguno

                return JsonResponse(response_data, status=status_code)

        except Exception as e:
            loggin_event(
                f'Error inesperado al eliminar pagos: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)

    def delete(self, request, payment_id):
        """Eliminar un pago específico por ID en la URL"""
        loggin_event(f'Eliminando pago {payment_id}')

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        # Verificar que el pago se pueda eliminar
        if payment.status in ['CONFIRMADO', 'RECHAZADO']:
            return JsonResponse(
                {'error': f'Cannot delete payment with status: {payment.status}'},
                status=400
            )

        try:
            with transaction.atomic():
                # Realizar soft delete
                payment.is_active = False
                payment.save()

                # También desactivar los detalles de pago asociados
                PaymentDetail.objects.filter(payment=payment).update(
                    is_active=False
                )

                loggin_event(f'Pago eliminado: {payment.payment_number}')

                return JsonResponse({
                    'message': 'Payment deleted successfully',
                    'payment_id': payment.id,
                    'payment_number': payment.payment_number
                }, status=200)

        except Exception as e:
            loggin_event(
                f'Error inesperado al eliminar pago: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)
