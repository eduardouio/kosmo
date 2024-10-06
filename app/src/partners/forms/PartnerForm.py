from django import forms
from partners.models import Partner


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
