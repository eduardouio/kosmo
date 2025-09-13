from django.views import View
from django.shortcuts import render, get_object_or_404
from trade.models.CreditNote import CreditNote


class CreditNoteDetailView(View):
	template_name = 'presentations/creditnote_presentation.html'

	def get(self, request, pk, *args, **kwargs):
		credit_note = get_object_or_404(CreditNote, pk=pk, is_active=True)
		context = {
			'title_page': f'Nota de Crédito {credit_note.num_credit_note}',
			'credit_note': credit_note,
			'details': credit_note.creditnotedetail_set.all(),
		}
		return render(request, self.template_name, context)


class CreditNoteListView(View):
	template_name = 'lists/creditnote_list.html'

	def get(self, request, *args, **kwargs):
		notes = CreditNote.objects.filter(is_active=True).order_by('-date')
		context = {
			'title_page': 'Notas de Crédito',
			'credit_notes': notes,
		}
		return render(request, self.template_name, context)
