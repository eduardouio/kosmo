from django import forms
from partners.models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'partner', 'name', 'position', 'phone', 'email', 'is_principal'
        ]
        widgets = {
            'partner': forms.Select(),
            'name': forms.TextInput(attrs={'maxlength': '255'}),
            'position': forms.TextInput(attrs={'maxlength': '255'}),
            'phone': forms.TextInput(attrs={'maxlength': '20'}),
            'email': forms.EmailInput(attrs={'maxlength': '255'}),
            'is_principal': forms.CheckboxInput(),
        }
