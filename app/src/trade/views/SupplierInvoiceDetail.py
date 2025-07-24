from common.AppLoger import loggin_event
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems
from django.shortcuts import get_object_or_404


# trade/supplier-invoice/<int:invoice_id>/
class SupplierInvoiceDetail(LoginRequiredMixin, TemplateView):
    template_name = "presentations/supplier_invoice_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        invoice_id = kwargs.get('invoice_id') or self.kwargs.get('invoice_id')

        try:
            # Obtener la factura usando get_object_or_404 para mejor manejo de errores
            invoice = get_object_or_404(Invoice, pk=invoice_id, is_active=True)
            
            # Verificar que sea una factura de compra
            if invoice.type_document != 'FAC_COMPRA':
                loggin_event(
                    f'La factura con ID: {invoice_id} no es una factura de compra',
                )
                context['error'] = 'La factura seleccionada no es una factura de proveedor.'
                context['title_page'] = 'Error - Factura de Proveedor'
                return context

            # Obtener los items de la factura
            invoice_items = InvoiceItems.get_invoice_items(invoice)

            # Obtener los box items para cada invoice item
            invoice_box_items = []
            for item in invoice_items:
                box_items = InvoiceBoxItems.get_box_items(item)
                invoice_box_items.extend(box_items)

            # Agregar datos al contexto
            context['invoice'] = invoice
            context['invoice_items'] = invoice_items
            context['invoice_box_items'] = invoice_box_items
            context['title_page'] = f'Factura de Proveedor {invoice.serie}-{invoice.consecutive or "000000"}'

        except Exception as e:
            loggin_event(f'Error al cargar factura de proveedor {invoice_id}: {str(e)}')
            context['error'] = f'Error al cargar la factura: {str(e)}'
            context['title_page'] = 'Error - Factura de Proveedor'

        return context

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)