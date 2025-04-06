from django.views.generic import TemplateView
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems
from datetime import datetime
from accounts.models.CustomUserModel import CustomUserModel


class TemplateInvoice(TemplateView):
    template_name = 'reports/invoice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = kwargs.get('id_invoice')
        invoice = Invoice.objects.get(pk=invoice_id)
        invoice_items = InvoiceItems.get_invoice_items(invoice)
        invoice_items_det = []
        for item in invoice_items:
            invoice_items_det.append({
                'item': item,
                'box_items': InvoiceBoxItems.get_box_items(item)
            })
        context['invoice'] = invoice
        context['invoice_items'] = invoice_items_det
        # Validar si el usuario creador de la factura existe
        id_user_created = invoice.id_user_created if invoice.id_user_created else 1
        context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
        context['now'] = datetime.now()
        return context