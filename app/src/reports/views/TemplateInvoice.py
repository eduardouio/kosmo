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
        context['totals'] = self.get_totals(invoice_items_det)
        # Validar si el usuario creador de la factura existe
        id_user_created = invoice.id_user_created if invoice.id_user_created else 1
        context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
        context['now'] = datetime.now()
        return context

    def get_totals(self, invoice_items_det):
        totals = {
            'total_hb': 0,
            'total_qb': 0,
            'total_fb': 0,
            'total_stems': 0,
            'pieces': len(invoice_items_det),
        }

        for item in invoice_items_det:
            totals['total_hb'] += item['item'].quantity if item['item'].box_model == 'HB' else 0
            totals['total_qb'] += item['item'].quantity if item['item'].box_model == 'QB' else 0
            totals['total_stems'] += item['item'].tot_stem_flower

        totals['total_fb'] = (totals['total_qb'] / 4) + (totals['total_hb'] / 2)

        return totals
