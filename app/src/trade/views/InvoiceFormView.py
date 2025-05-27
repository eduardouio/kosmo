from django.shortcuts import render, redirect
from django.http import Http404
from django.views import View
from django.contrib import messages
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems, STATUS_CHOICES
from common.AppLoger import loggin_event


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

        context = {
            'invoice': invoice,
            'invoice_items': invoice_items,
            'box_items': box_items,
            'status_choices': STATUS_CHOICES
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        invoice = Invoice.get_by_id(pk)
        # Actualizar campos de la cabecera
        invoice.date = request.POST.get('date')
        due_date = request.POST.get('due_date')
        invoice.due_date = due_date if due_date else None
        invoice.marking = request.POST.get('marking')
        invoice.awb = request.POST.get('awb')
        invoice.hawb = request.POST.get('hawb')
        invoice.dae_export = request.POST.get('dae_export')
        invoice.cargo_agency = request.POST.get('cargo_agency')
        delivery_date = request.POST.get('delivery_date')
        invoice.delivery_date = delivery_date if delivery_date else None
        weight = request.POST.get('weight')
        invoice.weight = weight if weight else None
        invoice.save()

        loggin_event(
            f"Factura {invoice.id} actualizada por {request.user.username}")
        messages.success(request, "Factura actualizada con éxito")

        return redirect('invoice_detail_presentation', pk=invoice.id)
