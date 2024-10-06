from django import forms
from .models import Bank


class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = [
            'partner', 'owner', 'id_owner', 'account_number', 'bank_name',
            'swift_code', 'iban', 'national_bank'
        ]
        widgets = {
            'partner': forms.Select(),
            'owner': forms.TextInput(attrs={'maxlength': '255'}),
            'id_owner': forms.TextInput(attrs={'maxlength': '15'}),
            'account_number': forms.TextInput(attrs={'maxlength': '50'}),
            'bank_name': forms.TextInput(attrs={'maxlength': '100'}),
            'swift_code': forms.TextInput(attrs={'maxlength': '50'}),
            'iban': forms.TextInput(attrs={'maxlength': '50'}),
            'national_bank': forms.CheckboxInput(),
        }
