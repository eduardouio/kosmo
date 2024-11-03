import json
from django.urls import reverse_lazy
from django import forms
from partners.models import Bank, Partner
from django.http import JsonResponse
from django.views.generic import (
    CreateView,
    UpdateView,
    ListView,
    DetailView,
    View,
    RedirectView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import serialize


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = [
            'partner', 'owner', 'id_owner', 'account_number', 'bank_name', 'swift_code', 
            'iban', 'national_bank', 'is_active', 'notes'
        ]
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'owner': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'id_owner': forms.TextInput(attrs={'maxlength': '15', 'class': 'form-control form-control-sm'}),
            'account_number': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'bank_name': forms.TextInput(attrs={'maxlength': '100', 'class': 'form-control form-control-sm'}),
            'swift_code': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'iban': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'national_bank': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


class BankCreateView(LoginRequiredMixin, CreateView):
    model = Bank
    form_class = BankForm
    template_name = 'forms/bank_form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(BankCreateView, self).get_context_data(*args, **kwargs)
        ctx['id_partner'] = self.kwargs.get('id_partner')
        ctx['title_section'] = 'Registrar Nuevo Banco'
        return ctx

    def get_form(self, form_class=None):
        form = super(BankCreateView, self).get_form(form_class)
        id_partner = self.kwargs.get('id_partner')
        partner = Partner.objects.get(pk=id_partner)
        if id_partner:
            form.fields['partner'].initial = partner
        return form

    def get_success_url(self):
        url = reverse_lazy('bank_detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


class BankUpdateView(LoginRequiredMixin, UpdateView):
    model = Bank
    form_class = BankForm
    template_name = 'forms/bank_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Banco {}'.format(self.object.bank_name)
        context['title_page'] = 'Actualizar Banco {}'.format(self.object.bank_name)
        context['action'] = None
        context['id_partner'] = self.object.pk
        return context

    def get_success_url(self):
        url = reverse_lazy('bank_detail', kwargs={'pk': self.object.pk})
        url = '{url}?action=updated'.format(url=url)
        return url


class BankDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        bank = Bank.objects.get(pk=kwargs['pk'])
        partner = bank.partner
        try:
            bank.delete()
            url = reverse_lazy('partner_detail', kwargs={'pk': partner.pk})
            return url + '?action=deleted_related'
        except Exception:
            url = reverse_lazy('bank_detail', kwargs={'pk': bank.pk})
            return url + '?action=no_delete_related'


class BankListView(LoginRequiredMixin, ListView):
    model = Bank
    template_name = 'lists/bank_list.html'
    context_object_name = 'banks'
    ordering = ['bank_name']

    def get_context_data(self, **kwargs):
        context = super(BankListView, self).get_context_data(**kwargs)
        context['title_section'] = 'Bancos'
        context['title_page'] = 'Listado de Bancos'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Banco Eliminado Exitosamente'
        return context


class BankDetailView(LoginRequiredMixin, DetailView):
    model = Bank
    template_name = 'presentations/bank_presentation.html'
    context_object_name = 'bank'

    def get_context_data(self, **kwargs):
        context = super(BankDetailView, self).get_context_data(**kwargs)
        context['title_section'] = self.object.bank_name
        context['title_page'] = self.object.bank_name
        context['action'] = self.request.GET.get('action')

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        message = ''

        if context['action'] == 'created':
            message = 'El banco ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El banco ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No se puede eliminar el registro. Existen dependencias'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
