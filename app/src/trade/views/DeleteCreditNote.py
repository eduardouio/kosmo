from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from trade.models.CreditNote import CreditNote
from trade.models.Payment import Payment, PaymentDetail
from common.AppLoger import loggin_event


class CreditNoteVoidView(View):
    def post(self, request, pk, *args, **kwargs):
        credit_note = get_object_or_404(CreditNote, pk=pk, is_active=True)
        
        try:
            with transaction.atomic():
                # Guardar referencia a la factura antes de anular
                invoice = credit_note.invoice
                
                # Anular el pago relacionado si existe
                if credit_note.id_payment:
                    try:
                        payment = Payment.objects.get(
                            pk=credit_note.id_payment
                        )
                        payment.status = 'ANULADO'
                        payment.is_active = False
                        payment.save()
                        
                        # Eliminar los detalles de pago para liberar el saldo
                        PaymentDetail.objects.filter(payment=payment).delete()
                        
                        loggin_event(
                            f"Pago {payment.pk} anulado correctamente para "
                            f"nota de crédito {credit_note.pk}"
                        )
                    except Payment.DoesNotExist:
                        loggin_event(
                            f"No se encontró el pago {credit_note.id_payment} "
                            f"para la nota de crédito {credit_note.pk}",
                            error=True
                        )
                
                # Anular la nota de crédito
                credit_note.status = 'ANULADO'
                credit_note.is_active = False
                credit_note.save()
                
                # Actualizar el estado de pago de la factura para
                # liberar el saldo
                if invoice:
                    invoice.update_payment_status()
                    loggin_event(
                        f"Estado de pago actualizado para factura "
                        f"{invoice.pk} después de anular nota de crédito "
                        f"{credit_note.pk}"
                    )
                
                user_id = (
                    request.user.pk if request.user.is_authenticated
                    else 'Anónimo'
                )
                loggin_event(
                    f"Nota de crédito {credit_note.pk} anulada correctamente "
                    f"por usuario {user_id}"
                )
                
            messages.success(
                request,
                'Nota de crédito anulada correctamente. '
                'El saldo de la factura ha sido liberado.'
            )
            return redirect(reverse('creditnote_list'))
            
        except Exception as e:
            loggin_event(
                f"Error al anular nota de crédito {credit_note.pk}: {str(e)}",
                error=True
            )
            messages.error(
                request,
                f'Error al anular la nota de crédito: {str(e)}'
            )
            return redirect(reverse('creditnote_list'))
