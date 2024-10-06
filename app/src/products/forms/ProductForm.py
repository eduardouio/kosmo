from django import forms
from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'image', 'variety', 'default_rend'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': '255'}),
            'image': forms.ClearableFileInput(),
            'variety': forms.TextInput(attrs={'maxlength': '255'}),
            'default_rend': forms.NumberInput(attrs={'step': '0.01'}),
        }
