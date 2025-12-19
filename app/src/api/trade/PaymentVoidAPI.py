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
        loggin_event("Anulando pagos")

        if not request.body:
            return JsonResponse({"error": "No data provided"}, status=400)
        payment_data = json.loads(request.body)

        if not payment_data:
            return JsonResponse({"error": "No data provided"}, status=400)

        if "payment_ids" not in payment_data:
            return JsonResponse({"error": "payment_ids field is required"}, status=400)

        payment_ids = payment_data["payment_ids"]
        if not isinstance(payment_ids, list) or len(payment_ids) == 0:
            return JsonResponse(
                {"error": "payment_ids must be a non-empty list"}, status=400
            )

        voided_payments = []
        not_found_payments = []
        cannot_void_payments = []

        with transaction.atomic():
            for payment_id in payment_ids:
                payment = Payment.objects.get(id=payment_id)

                if payment.status == "ANULADO":
                    cannot_void_payments.append(
                        {
                            "id": payment_id,
                            "payment_number": payment.payment_number,
                            "reason": "Payment is already voided",
                        }
                    )
                    continue

                revert_success = InvoiceBalance.revert_payment_from_invoices(payment_id)

                if not revert_success:
                    cannot_void_payments.append(
                        {
                            "id": payment_id,
                            "payment_number": payment.payment_number,
                            "reason": "Failed to revert invoice balances",
                        }
                    )
                    continue

                payment.status = "ANULADO"
                payment.save()

                from trade.models import Invoice

                Invoice.recalculate_payment_statuses_after_void(payment_id)

                voided_payments.append(
                    {"id": payment.id, "payment_number": payment.payment_number}
                )

                loggin_event(f"Pago anulado: {payment.payment_number}")

            response_data = {
                "message": (f"{len(voided_payments)} payments voided " "successfully")
            }

            if voided_payments:
                response_data["voided_payments"] = voided_payments

            if not_found_payments:
                response_data["not_found_payments"] = not_found_payments

            if cannot_void_payments:
                response_data["cannot_void_payments"] = cannot_void_payments

            if len(voided_payments) == len(payment_ids):
                status_code = 200
            elif len(voided_payments) > 0:
                status_code = 207
            else:
                status_code = 400

            return JsonResponse(response_data, status=status_code)

    def delete(self, request, payment_id):
        """Anular un pago específico por ID en la URL"""
        loggin_event(f"Anulando pago {payment_id}")

        payment = Payment.objects.get(id=payment_id)

        if payment.status == "ANULADO":
            return JsonResponse({"error": "Payment is already voided"}, status=400)

        with transaction.atomic():

            revert_success = InvoiceBalance.revert_payment_from_invoices(payment_id)

            if not revert_success:
                return JsonResponse(
                    {"error": "Failed to revert invoice balances"}, status=500
                )

            payment.status = "ANULADO"
            payment.save()

            from trade.models import Invoice

            Invoice.recalculate_payment_statuses_after_void(payment_id)

            loggin_event(f"Pago anulado: {payment.payment_number}")

            return JsonResponse(
                {
                    "message": "Payment voided successfully",
                    "payment_id": payment.id,
                    "payment_number": payment.payment_number,
                },
                status=200,
            )
