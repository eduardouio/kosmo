from django import forms
from .models import Order, OrderItems

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'partner', 'type_document', 'parent_order', 'num_order', 'delivery_date',
            'status', 'discount', 'total_price', 'qb_total', 'hb_total'
        ]
        widgets = {
            'partner': forms.Select(),
            'type_document': forms.Select(choices=TYPE_DOCUMENT_CHOICES),
            'parent_order': forms.Select(),
            'num_order': forms.TextInput(attrs={'maxlength': '50'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(choices=STATUS_CHOICES),
            'discount': forms.NumberInput(attrs={'step': '0.01'}),
            'total_price': forms.NumberInput(attrs={'step': '0.01'}),
            'qb_total': forms.NumberInput(),
            'hb_total': forms.NumberInput(),
        }

class OrderItemsForm(forms.ModelForm):
    class Meta:
        model = OrderItems
        fields = [
            'order', 'stock_detail', 'box_quantity', 'line_price', 
            'qty_stem_flower', 'box_model'
        ]
        widgets = {
            'order': forms.Select(),
            'stock_detail': forms.Select(),
            'box_quantity': forms.NumberInput(),
            'line_price': forms.NumberInput(attrs={'step': '0.01'}),
            'qty_stem_flower': forms.NumberInput(),
            'box_model': forms.Select(choices=BOX_CHOICES),
        }
