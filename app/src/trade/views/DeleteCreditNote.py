from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from trade.models.CreditNote import CreditNote
from trade.models.Payment import Payment, PaymentDetail


class CreditNoteVoidView(View):
	def post(self, request, pk, *args, **kwargs):
		credit_note = get_object_or_404(CreditNote, pk=pk, is_active=True)
		with transaction.atomic():
			if credit_note.id_payment:
				try:
					payment = Payment.objects.get(pk=credit_note.id_payment)
					payment.status = 'ANULADO'
					payment.is_active = False
					payment.save()
					PaymentDetail.objects.filter(payment=payment).delete()
				except Payment.DoesNotExist:
					pass
			credit_note.status = 'ANULADO'
			credit_note.is_active = False
			credit_note.save()
		messages.success(request, 'Nota de crédito anulada correctamente.')
		return redirect(reverse('creditnote_list'))
