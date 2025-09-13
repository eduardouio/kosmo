from django import forms
from django.forms import inlineformset_factory
from trade.models.CreditNote import CreditNote, CreditNoteDetail
from partners.models import Partner


class CreditNoteForm(forms.ModelForm):
    # Campo adicional para seleccionar cliente
    partner = forms.ModelChoiceField(
        queryset=Partner.objects.filter(
            is_active=True,
            type_partner='CLIENTE'
        ),
        empty_label="Seleccione un cliente...",
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'id': 'id_partner'
        }),
        label='Cliente'
    )
    
    class Meta:
        model = CreditNote
        fields = [
            'invoice', 'date', 'amount', 'reason', 'notes'
        ]
        widgets = {
            'invoice': forms.Select(attrs={
                'class': 'form-control form-select',
                'id': 'id_invoice'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'id': 'id_amount',
                'readonly': True
            }),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicialmente el select de facturas está vacío
        self.fields['invoice'].queryset = (
            self.fields['invoice'].queryset.none()
        )
        self.fields['invoice'].widget.attrs.update({
            'disabled': True
        })

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError('El monto debe ser mayor a 0')
        return amount


class CreditNoteDetailForm(forms.ModelForm):
    class Meta:
        model = CreditNoteDetail
        fields = [
            'description', 'quantity', 'unit_price', 'total_price'
        ]
        widgets = {
            'description': forms.TextInput(attrs={
                'maxlength': '200',
                'class': 'form-control'
            }),
            'quantity': forms.NumberInput(attrs={
                'step': '1',
                'min': '1',
                'class': 'form-control'
            }),
            'unit_price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control'
            }),
            'total_price': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned = super().clean()
        qty = cleaned.get('quantity') or 0
        unit = cleaned.get('unit_price') or 0
        total = cleaned.get('total_price')
        calc = qty * unit
        if total is None:
            cleaned['total_price'] = calc
        else:
            # tolerancia
            if calc and abs(calc - total) > 0.01:
                self.add_error(
                    'total_price',
                    'No coincide con cantidad * precio unitario'
                )
        return cleaned


CreditNoteDetailFormSet = inlineformset_factory(
    CreditNote,
    CreditNoteDetail,
    form=CreditNoteDetailForm,
    extra=1,
    can_delete=True
)
