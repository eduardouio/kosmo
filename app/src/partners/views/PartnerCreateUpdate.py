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
    # Campo de formulario (no directamente del modelo) redefinido como ChoiceField
    # para mostrar un select de usuarios con rol VENDEDOR. El valor será el id
    # del usuario y se almacenará en los campos del modelo: id_seller y seller.
    seller = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    class Meta:
        model = Partner
        fields = [
            'business_tax_id', 'name', 'status', 'date_aproved', 'country',
            'city', 'zip_code', 'address', 'phone', 'email', 'type_partner',
            'credit_term', 'website', 'skype', 'dispatch_address',
            'dispatch_days', 'cargo_reference', 'consolidate', 'is_active',
            'notes', 'email_payment', 'reference_1', 'contact_reference_1',
            'default_profit_margin', 'is_profit_margin_included',
            'contact_reference_2', 'short_name', 'is_verified', 'seller',
            'reference_2', 'area_code', 'phone_reference_1',
            'prompt_disponibility', 'phone_reference_2'
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
            'status': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'date_aproved': forms.DateInput(attrs={'class': 'form-control form-control-sm', 'type': 'date'}),
            'prompt_disponibility': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Construir lista de vendedores (usuarios con rol VENDEDOR)
        sellers = CustomUserModel.get_sellers()
        # Valor = id del usuario; Etiqueta = Nombre completo o email
        seller_choices = [
            (
                seller.pk,
                (seller.get_full_name().strip()
                 if seller.get_full_name() else seller.email)
            )
            for seller in sellers
        ]
        self.fields['seller'].choices = [('', '---------')] + seller_choices
        # Pre-cargar valor al editar si existe
        if self.instance and self.instance.id_seller:
            self.initial['seller'] = self.instance.id_seller
        # Si no hay id_seller pero sí texto en seller intentamos emparejar
        elif self.instance and self.instance.seller:
            match = next((u for u in sellers if (u.get_full_name().strip(
            ) if u.get_full_name() else u.email) == self.instance.seller), None)
            if match:
                self.initial['seller'] = match.pk

    def save(self, commit=True):
        instance = super().save(commit=False)
        seller_id = self.cleaned_data.get('seller')
        if instance.type_partner == 'CLIENTE' and seller_id:
            try:
                user = CustomUserModel.objects.get(pk=seller_id)
                full_name = user.get_full_name().strip()
                instance.id_seller = user.pk
                instance.seller = full_name if full_name else user.email
            except CustomUserModel.DoesNotExist:
                instance.id_seller = None
                instance.seller = None
        else:
            # Para proveedores u opción vacía limpiamos los campos
            instance.id_seller = None
            instance.seller = None

        if commit:
            instance.save()
            self.save_m2m()
        return instance


# socios/nuevo/
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
        form.instance.is_verified = True
        return super().form_valid(form)


# socios/actualizar-parent/<int:pk>/
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


# socios/actualizar/<int:pk>/
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
