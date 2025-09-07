from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib import messages
from django import forms
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems, STATUS_CHOICES
from common.AppLoger import loggin_event


# trade/invoice-form/<int:pk>/ y trade/invoice/update/<int:pk>/
class InvoiceNotesForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-sm',
                    'rows': 3,
                    'placeholder': 'Información interna o comentarios'
                }
            )
        }


class InvoiceFormView(View):
    template_name = 'forms/invoice_form.html'

    def get(self, request, pk):
        invoice = Invoice.get_by_id(pk)
        if not invoice:
            raise Http404("La factura no existe")

        invoice_items = InvoiceItems.get_invoice_items(invoice)

        # Contar los items de la caja para cada elemento de factura
        for item in invoice_items:
            item.box_items_count = InvoiceBoxItems.objects.filter(
                invoice_item=item,
                is_active=True
            ).count()

        box_items = InvoiceBoxItems.objects.filter(
            invoice_item__invoice=invoice,
            is_active=True
        )

        # Calcular el total para cada elemento de caja
        for box_item in box_items:
            box_item.calculated_total = (
                box_item.unit_price * box_item.qty_stem_flower *
                InvoiceItems.objects.get(id=box_item.invoice_item.id).quantity
            )

        notes_form = InvoiceNotesForm(instance=invoice)
        context = {
            'invoice': invoice,
            'invoice_items': invoice_items,
            'box_items': box_items,
            'status_choices': STATUS_CHOICES,
            'form': notes_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        invoice = Invoice.get_by_id(pk)
        if not invoice:
            raise Http404("La factura no existe")

        # Actualizar campos de la cabecera
        invoice.date = request.POST.get('date')
        invoice.due_date = request.POST.get('due_date') or None
        invoice.marking = request.POST.get('marking')
        invoice.awb = request.POST.get('awb')
        invoice.hawb = request.POST.get('hawb')
        invoice.po_number = request.POST.get('po_number')
        invoice.dae_export = request.POST.get('dae_export')
        invoice.destination_country = request.POST.get('destination_country')
        invoice.cargo_agency = request.POST.get('cargo_agency')
        invoice.delivery_date = request.POST.get('delivery_date') or None
        weight = request.POST.get('weight')
        invoice.weight = weight if weight else None
        # Procesar notas via ModelForm para validación
        notes_form = InvoiceNotesForm(request.POST, instance=invoice)
        if notes_form.is_valid():
            notes_form.save()
        else:
            invoice_items = InvoiceItems.get_invoice_items(invoice)
            box_items = InvoiceBoxItems.objects.filter(
                invoice_item__invoice=invoice,
                is_active=True
            )
            messages.error(request, "Errores al actualizar las notas.")
            return render(
                request,
                self.template_name,
                {
                    'invoice': invoice,
                    'invoice_items': invoice_items,
                    'box_items': box_items,
                    'status_choices': STATUS_CHOICES,
                    'form': notes_form,
                }
            )

        loggin_event(
            f"Factura {invoice.id} actualizada por {request.user.username}"
        )
        messages.success(request, "Factura actualizada con éxito")
        return redirect('invoice_detail_presentation', pk=invoice.id)
