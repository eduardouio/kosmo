from django import forms
from .models import Payment


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            'invoices', 'date', 'amount', 'method', 'bank', 'nro_account', 'nro_operation'
        ]
        widgets = {
            'invoices': forms.SelectMultiple(),
            'date': forms.DateInput(attrs={'type': 'date'}),
            'amount': forms.NumberInput(attrs={'step': '0.01'}),
            'method': forms.Select(choices=METHOD_CHOICES),
            'bank': forms.TextInput(attrs={'maxlength': '50'}),
            'nro_account': forms.TextInput(attrs={'maxlength': '50'}),
            'nro_operation': forms.TextInput(attrs={'maxlength': '50'}),
        }
