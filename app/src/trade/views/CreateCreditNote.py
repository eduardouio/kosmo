from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from trade.forms import CreditNoteForm, CreditNoteDetailFormSet
from trade.models.CreditNote import CreditNote
from trade.models.Invoice import Invoice
from trade.models.Payment import Payment, PaymentDetail


class CreditNoteCreateView(View):
	template_name = 'forms/creditnote_form.html'

	def get(self, request, *args, **kwargs):
		invoice_id = request.GET.get('invoice')
		initial = {}
		if invoice_id:
			invoice = get_object_or_404(Invoice, pk=invoice_id)
			initial['invoice'] = invoice
		form = CreditNoteForm(initial=initial)
		formset = CreditNoteDetailFormSet()
		context = {
			'form': form,
			'formset': formset,
			'title_page': 'Nueva Nota de Crédito',
		}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		form = CreditNoteForm(request.POST)
		formset = CreditNoteDetailFormSet(request.POST)
		if form.is_valid() and formset.is_valid():
			with transaction.atomic():
				credit_note: CreditNote = form.save(commit=False)
				# Monto total desde detalles si existen
				total_from_details = 0
				for f in formset.forms:
					if not f.cleaned_data or f.cleaned_data.get('DELETE'):
						continue
					qty = f.cleaned_data.get('quantity') or 0
					unit = f.cleaned_data.get('unit_price') or 0
					total_from_details += qty * unit
				if total_from_details and abs(total_from_details - credit_note.amount) > 0.01:
					credit_note.amount = total_from_details
				credit_note.save()
				formset.instance = credit_note
				formset.save()

				invoice = credit_note.invoice
				payment = Payment.objects.create(
					date=credit_note.date,
					amount=credit_note.amount,
					method='NC',
					type_transaction='INGRESO',
					status='CONFIRMADO',
					notes=f'Generado por NC {credit_note.num_credit_note}'
				)
				PaymentDetail.objects.create(
					payment=payment,
					invoice=invoice,
					amount=credit_note.amount
				)
				credit_note.id_payment = payment.id
				credit_note.save()
			messages.success(request, 'Nota de crédito creada correctamente.')
			return redirect(reverse('creditnote_detail', args=[credit_note.pk]))
		messages.error(request, 'Por favor corrige los errores del formulario.')
		return render(request, self.template_name, {
			'form': form,
			'formset': formset,
			'title_page': 'Nueva Nota de Crédito'
		})
