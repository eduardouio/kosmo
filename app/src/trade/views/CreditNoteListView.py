from django.views import View
from django.shortcuts import render, get_object_or_404
from trade.models.CreditNote import CreditNote


class CreditNoteListView(View):
	template_name = 'lists/creditnote_list.html'

	def get(self, request, *args, **kwargs):
		notes = CreditNote.objects.filter(is_active=True).order_by('-date')
		context = {
			'title_page': 'Notas de Crédito',
			'credit_notes': notes,
		}
		return render(request, self.template_name, context)
