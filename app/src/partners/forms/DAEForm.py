from django import forms
from .models import DAE


class DAEForm(forms.ModelForm):
    class Meta:
        model = DAE
        fields = [
            'partner', 'dae', 'date_begin', 'date_end'
        ]
        widgets = {
            'partner': forms.Select(),
            'dae': forms.TextInput(attrs={'maxlength': '50'}),
            'date_begin': forms.DateInput(attrs={'type': 'date'}),
            'date_end': forms.DateInput(attrs={'type': 'date'}),
        }
