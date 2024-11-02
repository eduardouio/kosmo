
import json
from django.urls import reverse_lazy
from django import forms
from partners.models import Partner
from django.http import JsonResponse
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    DetailView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize
from partners.models import Partner, Bank, Contact, DAE


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'business_tax_id', 'name', 'country', 'city', 'zip_code', 'address',
            'phone', 'email', 'type_partner', 'credit_term', 'website', 'skype',
            'dispatch_address', 'dispatch_days', 'cargo_reference', 'consolidate'
        ]
        widgets = {
            'business_tax_id': forms.TextInput(attrs={'maxlength': '15'}),
            'name': forms.TextInput(attrs={'maxlength': '255'}),
            'country': forms.TextInput(attrs={'maxlength': '50'}),
            'city': forms.TextInput(attrs={'maxlength': '50'}),
            'zip_code': forms.TextInput(attrs={'maxlength': '10'}),
            'address': forms.TextInput(attrs={'maxlength': '255'}),
            'phone': forms.TextInput(attrs={'maxlength': '20'}),
            'email': forms.EmailInput(attrs={'maxlength': '255'}),
            'type_partner': forms.Select(),
            'credit_term': forms.NumberInput(),
            'website': forms.URLInput(),
            'skype': forms.TextInput(attrs={'maxlength': '50'}),
            'dispatch_address': forms.TextInput(attrs={'maxlength': '255'}),
            'dispatch_days': forms.NumberInput(),
            'cargo_reference': forms.TextInput(attrs={'maxlength': '255'}),
            'consolidate': forms.CheckboxInput(),
        }


class PartnerCreateView(LoginRequiredMixin, CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'forms/partner-form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(PartnerCreateView, self).get_context_data(*args, **kwargs)
        ctx['title_bar'] = 'Create Partner'
        return ctx

    def get_success_url(self):
        url = reverse_lazy('partner-detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


class PartnerUpdateParent(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.objects.get(pk=kwargs['pk'])
        partner_parent = Partner.get_partner_by_id(data['id'])
        if data['selected']:
            partner.partner.add(partner_parent)
        else:
            partner.partner.remove(partner_parent)

        return JsonResponse({'status': 'ok'})


class PartnerUpdateView(LoginRequiredMixin, UpdateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'forms/partner-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )
        context['title_page'] = 'Actualizar Socio de Negocio {}'.format(
            self.object.business_tax_id
        )

        return context

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class PartnerDeleteView(LoginRequiredMixin, DeleteView):
    def get_redirect_url(self, *args, **kwargs):
        partner = Partner.objects.get(pk=kwargs['pk'])
        try:
            partner.delete()
            url = reverse_lazy('partner_list')
            return f'{url}?action=deleted'
        except Exception as e:
            url = reverse_lazy('partner_detail', kwargs={'pk': kwargs['pk']})
            return '{url}?action=no_delete'.format(url=url)


class PartnerListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'lists/partner_list.html'
    context_object_name = 'partners'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super(PartnerListView, self).get_context_data(**kwargs)
        context['title_section'] = 'Socios de Negocio'
        context['title_page'] = 'Listado de Socios de Negocio'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Socio Eliminado Exitosamente'
        return context


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
        parent_suppliers = Partner.get_parent_suppliers(self.object)
        context['parent_supliers'] = json.dumps([{
            'suplier': serialize('json', [i['suplier']]),
            'selected': i['selected']
        } for i in parent_suppliers])

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

        context['message'] = message
        return context
