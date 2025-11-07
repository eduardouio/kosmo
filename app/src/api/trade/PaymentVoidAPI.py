import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction

from trade.models import Payment
from common.AppLoger import loggin_event
from common.InvoiceBalance import InvoiceBalance


class PaymentVoidAPI(View):

    def post(self, request):
        """Anular pagos cambiando estado a ANULADO y revirtiendo saldos"""
        loggin_event('Anulando pagos')

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

        voided_payments = []
        not_found_payments = []
        cannot_void_payments = []

        try:
            with transaction.atomic():
                for payment_id in payment_ids:
                    try:
                        payment = Payment.objects.get(id=payment_id)

                        # Verificar que el pago se pueda anular
                        # No se pueden anular pagos ya anulados
                        if payment.status == 'ANULADO':
                            cannot_void_payments.append({
                                'id': payment_id,
                                'payment_number': payment.payment_number,
                                'reason': 'Payment is already voided'
                            })
                            continue

                        # Revertir los saldos de las facturas antes de anular
                        revert_success = (
                            InvoiceBalance.revert_payment_from_invoices(
                                payment_id
                            )
                        )
                        
                        if not revert_success:
                            cannot_void_payments.append({
                                'id': payment_id,
                                'payment_number': payment.payment_number,
                                'reason': 'Failed to revert invoice balances'
                            })
                            continue

                        # Cambiar estado del pago a ANULADO
                        payment.status = 'ANULADO'
                        payment.save()

                        # Recalcular estados de facturas afectadas
                        from trade.models import Invoice
                        Invoice.recalculate_payment_statuses_after_void(payment_id)

                        voided_payments.append({
                            'id': payment.id,
                            'payment_number': payment.payment_number
                        })

                        loggin_event(
                            f'Pago anulado: {payment.payment_number}')

                    except Payment.DoesNotExist:
                        not_found_payments.append(payment_id)
                        continue

                # Preparar respuesta
                response_data = {
                    'message': (f'{len(voided_payments)} payments voided '
                                'successfully')
                }

                if voided_payments:
                    response_data['voided_payments'] = voided_payments

                if not_found_payments:
                    response_data['not_found_payments'] = not_found_payments

                if cannot_void_payments:
                    response_data['cannot_void_payments'] = (
                        cannot_void_payments
                    )

                # Determinar código de estado
                if len(voided_payments) == len(payment_ids):
                    status_code = 200  # Todo se anuló correctamente
                elif len(voided_payments) > 0:
                    status_code = 207  # Anulación parcial
                else:
                    status_code = 400  # No se pudo anular ninguno

                return JsonResponse(response_data, status=status_code)

        except Exception as e:
            loggin_event(
                f'Error inesperado al anular pagos: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)

    def delete(self, request, payment_id):
        """Anular un pago específico por ID en la URL"""
        loggin_event(f'Anulando pago {payment_id}')

        try:
            payment = Payment.objects.get(id=payment_id)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

        # Verificar que el pago se pueda anular
        if payment.status == 'ANULADO':
            return JsonResponse(
                {'error': 'Payment is already voided'},
                status=400
            )

        try:
            with transaction.atomic():
                # Revertir los saldos de las facturas antes de anular
                revert_success = InvoiceBalance.revert_payment_from_invoices(
                    payment_id
                )

                if not revert_success:
                    return JsonResponse(
                        {
                            'error': 'Failed to revert invoice balances'
                        },
                        status=500
                    )

                # Cambiar estado del pago a ANULADO
                payment.status = 'ANULADO'
                payment.save()

                # Recalcular estados de facturas afectadas
                from trade.models import Invoice
                Invoice.recalculate_payment_statuses_after_void(payment_id)

                loggin_event(f'Pago anulado: {payment.payment_number}')

                return JsonResponse({
                    'message': 'Payment voided successfully',
                    'payment_id': payment.id,
                    'payment_number': payment.payment_number
                }, status=200)

        except Exception as e:
            loggin_event(
                f'Error inesperado al anular pago: {str(e)}', error=True)
            return JsonResponse({'error': 'Internal server error'}, status=500)
