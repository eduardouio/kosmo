from common.AppLoger import loggin_event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from trade.models import Invoice
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.dateparse import parse_date
from decimal import Decimal


# trade/supplier-invoice/update/<int:invoice_id>/
class InvoiceSupplierUpdate(LoginRequiredMixin, TemplateView):
    template_name = "forms/invoice_supplier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        invoice_id = kwargs.get('invoice_id') or kwargs.get('pk')
        invoice = get_object_or_404(Invoice, pk=invoice_id, is_active=True)

        if invoice.type_document != 'FAC_COMPRA':
            context['error'] = 'La factura seleccionada no es una factura de proveedor.'
            context['title_page'] = 'Error - Editar Factura'
            return context

        if invoice.status != 'PENDIENTE':
            context['error'] = 'Solo se pueden editar facturas en estado PENDIENTE.'
            context['title_page'] = 'Error - Editar Factura'
            return context

        context['invoice'] = invoice
        context['title_page'] = f'Editar Cabeceras Factura de Compra - Factura {invoice.serie}-{invoice.consecutive or "000000"}'
        return context

    def post(self, request, *args, **kwargs):
        invoice_id = kwargs.get('invoice_id') or kwargs.get('pk')

        invoice = get_object_or_404(Invoice, pk=invoice_id, is_active=True)

        if invoice.type_document != 'FAC_COMPRA':
            messages.error(
                request, 'La factura seleccionada no es una factura de proveedor.')
            return redirect('supplier_invoice_detail', invoice_id=invoice_id)

        if invoice.status != 'PENDIENTE':
            messages.error(
                request, 'Solo se pueden editar facturas en estado PENDIENTE.')
            return redirect('supplier_invoice_detail', invoice_id=invoice_id)

        if 'edit_headers' in request.POST:
            # Campos básicos
            invoice.num_invoice = request.POST.get('num_invoice', '').strip()

            # Fechas
            due_date = request.POST.get('due_date')
            if due_date:
                invoice.due_date = parse_date(due_date)
            else:
                invoice.due_date = None

            delivery_date = request.POST.get('delivery_date')
            if delivery_date:
                invoice.delivery_date = parse_date(delivery_date)
            else:
                invoice.delivery_date = None

            invoice.save()

            loggin_event(
                f'Cabeceras de factura {invoice_id} actualizadas por usuario {request.user.username}')
            messages.success(
                request, 'Las cabeceras de la factura han sido actualizadas exitosamente.')

            return redirect('supplier_invoice_detail', invoice_id=invoice_id)

        return redirect('supplier_invoice_detail', invoice_id=invoice_id)
