from django import forms
from trade.models.Invoice import Invoice, InvoiceItems


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'order', 'partner', 'num_invoice', 'type_document',
            'type_invoice', 'date', 'due_date', 'total_price', 'qb_total',
            'hb_total', 'awb', 'dae_export', 'hawb', 'cargo_agency',
            'delivery_date', 'weight', 'status', 'notes'
        ]
        widgets = {
            'order': forms.Select(),
            'partner': forms.Select(),
            'num_invoice': forms.NumberInput(),
            'type_document': forms.Select(),
            'type_invoice': forms.Select(),
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'total_price': forms.NumberInput(attrs={'step': '0.01'}),
            'qb_total': forms.NumberInput(),
            'hb_total': forms.NumberInput(),
            'awb': forms.TextInput(attrs={'maxlength': '50'}),
            'dae_export': forms.TextInput(attrs={'maxlength': '50'}),
            'hawb': forms.TextInput(attrs={'maxlength': '50'}),
            'cargo_agency': forms.TextInput(attrs={'maxlength': '50'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date'}),
            'weight': forms.NumberInput(attrs={'step': '0.01'}),
            'status': forms.Select(),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class InvoiceItemsForm(forms.ModelForm):
    class Meta:
        model = InvoiceItems
        fields = [
            'invoice', 'order_item', 'qty_stem_flower', 'line_price',
            'line_discount', 'box'
        ]
        widgets = {
            'invoice': forms.Select(),
            'order_item': forms.Select(),
            'qty_stem_flower': forms.NumberInput(),
            'line_price': forms.NumberInput(attrs={'step': '0.01'}),
            'line_discount': forms.NumberInput(attrs={'step': '0.01'}),
            'box': forms.Select(),
        }
