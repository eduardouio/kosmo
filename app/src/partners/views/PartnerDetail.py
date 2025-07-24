import json
from partners.models import Partner
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from partners.models import Partner, Bank, Contact, DAE


# socios/<int:pk>/
class PartnerDetailView(LoginRequiredMixin, DetailView):
    model = Partner
    template_name = 'presentations/partner_presentation.html'
    context_object_name = 'partner'

    def get_context_data(self, **kwargs):
        context = super(PartnerDetailView, self).get_context_data(**kwargs)
        context['title_section'] = self.object.name
        context['title_page'] = self.object.name
        context['last_dae'] = DAE.get_last_by_partner(self.object)
        context['banks'] = Bank.get_by_partner(self.object)
        context['contacts'] = Contact.get_by_partner(self.object)
        context['action'] = self.request.GET.get('action')
        parent_suppliers = Partner.get_parent_suppliers(self.object)
        context['parent_supliers'] = json.dumps([{
            'suplier': serialize('json', [i['suplier']]),
            'selected': i['selected']
        } for i in parent_suppliers])
        context['source_page'] = 'clientes' if self.object.type_partner == 'CLIENTE' else 'proveedores'

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        message = ''

        if context['action'] == 'created':
            message = 'El socio de negocio ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El socio de negocio ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No sel puede eliminar el registro. Existen dependencias'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'
        elif context['action'] == 'deleted_related':
            message = 'El registro ha sido eliminado exitosamente'

        context['message'] = message
        return context
