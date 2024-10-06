from django import forms
from .models import StockDay, StockDetail


class StockDayForm(forms.ModelForm):
    class Meta:
        model = StockDay
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }


class StockDetailForm(forms.ModelForm):
    class Meta:
        model = StockDetail
        fields = [
            'stock_day', 'product', 'partner', 'color', 'length', 'box_quantity', 
            'qty_stem_flower', 'box_model', 'stem_cost_price'
        ]
        widgets = {
            'stock_day': forms.Select(),
            'product': forms.Select(),
            'partner': forms.Select(),
            'color': forms.TextInput(attrs={'maxlength': '255'}),
            'length': forms.NumberInput(),
            'box_quantity': forms.NumberInput(),
            'qty_stem_flower': forms.NumberInput(),
            'box_model': forms.Select(),
            'stem_cost_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
