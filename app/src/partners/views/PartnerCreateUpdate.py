import json
from django.urls import reverse_lazy
from django import forms
from partners.models import Partner
from django.http import JsonResponse
from django.views.generic import (
    CreateView,
    UpdateView,
    View,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner
from accounts.models import CustomUserModel


class PartnerForm(forms.ModelForm):
    class Meta:
        model = Partner
        fields = [
            'business_tax_id', 'name', 'status', 'date_aproved', 'country', 'city', 'zip_code',
            'address', 'phone', 'email', 'type_partner', 'credit_term',
            'website', 'skype', 'dispatch_address', 'dispatch_days',
            'cargo_reference', 'consolidate', 'is_active', 'notes',
            'email_payment','reference_1', 'contact_reference_1',
            'default_profit_margin', 'is_profit_margin_included',
            'reference_2','area_code','phone_reference_1', 'phone_reference_2',
            'contact_reference_2', 'short_name', 'is_verified', 'seller'
        ]
        widgets = {
            'business_tax_id': forms.TextInput(attrs={'maxlength': '15', 'class': 'form-control form-control-sm'}),
            'name': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'country': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'city': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'zip_code': forms.TextInput(attrs={'maxlength': '10', 'class': 'form-control form-control-sm'}),
            'address': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'maxlength': '20', 'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'type_partner': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'credit_term': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'website': forms.URLInput(attrs={'class': 'form-control form-control-sm'}),
            'skype': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'dispatch_address': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'dispatch_days': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'cargo_reference': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'consolidate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
            'is_verified': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'default_profit_margin': forms.NumberInput(attrs={'class': 'form-control form-control-sm'}),
            'is_profit_margin_included': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_payment': forms.EmailInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'reference_1': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'contact_reference_1': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'reference_2': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'contact_reference_2': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'area_code': forms.TextInput(attrs={'maxlength': '10', 'class': 'form-control form-control-sm'}),
            'phone_reference_1': forms.TextInput(attrs={'maxlength': '20', 'class': 'form-control form-control-sm'}),
            'phone_reference_2': forms.TextInput(attrs={'maxlength': '20', 'class': 'form-control form-control-sm'}),
            'short_name': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'seller': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'status': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'date_aproved': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sellers = CustomUserModel.get_sellers()
        seller_choices = [(seller.get_full_name() if seller.get_full_name() else seller.email, seller.get_full_name() if seller.get_full_name() else seller.email) for seller in sellers]
        self.fields['seller'].choices = [('', '---------')] + seller_choices
        

class PartnerCreateView(LoginRequiredMixin, CreateView):
    model = Partner
    form_class = PartnerForm
    template_name = 'forms/partner-form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(PartnerCreateView, self).get_context_data(*args, **kwargs)
        ctx['title_bar'] = 'Create Partner'
        return ctx

    def get_success_url(self):
        url = reverse_lazy('partner_detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url

    def form_valid(self, form):
        # Establecer valores por defecto para nuevo socio
        form.instance.status = 'APROBADO'
        return super().form_valid(form)


class PartnerUpdateParent(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        partner = Partner.objects.get(pk=kwargs['pk'])
        partner_parent = Partner.get_by_id(data['id'])
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
        url = '{url}?action=updated'.format(url=url)
        return url
