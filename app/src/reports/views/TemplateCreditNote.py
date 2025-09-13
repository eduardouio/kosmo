from django.views.generic import TemplateView
from trade.models import CreditNote, CreditNoteDetail
from datetime import datetime
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event


class TemplateCreditNote(TemplateView):
    template_name = 'reports/creditnote.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        credit_note_id = kwargs.get('id_credit_note')
        
        try:
            credit_note = CreditNote.objects.select_related(
                'invoice', 'invoice__partner'
            ).get(pk=credit_note_id)
            details = CreditNoteDetail.objects.filter(credit_note=credit_note)
            
            context['credit_note'] = credit_note
            context['details'] = details
            
            # Obtener el usuario que creó la nota de crédito
            id_user_created = (
                credit_note.id_user_created
                if credit_note.id_user_created else 1
            )
            context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
            context['now'] = datetime.now()
            
        except CreditNote.DoesNotExist:
            loggin_event(
                f"Nota de crédito con ID {credit_note_id} no encontrada",
                error=True
            )
            context['credit_note'] = None
            context['details'] = []
        except Exception as e:
            loggin_event(
                f"Error al obtener la nota de crédito "
                f"{credit_note_id}: {str(e)}",
                error=True
            )
            context['credit_note'] = None
            context['details'] = []

        return context
