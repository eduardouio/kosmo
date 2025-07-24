from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems


# trade/invoice/<int:pk>/
class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'presentations/invoice_presentation.html'
    context_object_name = 'invoice'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_active:
            raise Http404("La factura no existe o ha sido eliminada")
        return obj

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context['title_section'] = f"Factura {self.object.num_invoice or self.object.id}"
        context['title_page'] = f"Factura {self.object.num_invoice or self.object.id}"
        context['invoice_items'] = InvoiceItems.get_invoice_items(self.object)

        # Calcular totales para cada box_item
        box_items = InvoiceBoxItems.objects.filter(
            invoice_item__invoice=self.object, is_active=True
        )
        for box_item in box_items:
            box_item.calculated_total = box_item.total_price + \
                (box_item.profit_margin * box_item.qty_stem_flower)

        context['box_items'] = box_items

        # Añadir datos de envío directamente del objeto invoice
        context['awb'] = self.object.awb
        context['hawb'] = self.object.hawb
        context['dae_export'] = self.object.dae_export
        context['cargo_agency'] = self.object.cargo_agency
        context['delivery_date'] = self.object.delivery_date
        context['weight'] = self.object.weight
        context['action'] = self.request.GET.get('action')

        # Calcular días hasta vencimiento
        context['days_to_due'] = self.object.days_to_due

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        message = ''

        if context['action'] == 'created':
            message = 'La factura ha sido creada con éxito.'
        elif context['action'] == 'updated':
            message = 'La factura ha sido actualizada con éxito.'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'
        elif context['action'] == 'deleted_related':
            message = 'El registro ha sido eliminado exitosamente.'
        elif context['action'] == 'paid':
            message = 'La factura ha sido marcada como pagada.'
        elif context['action'] == 'cancelled':
            message = 'La factura ha sido anulada.'

        context['message'] = message
        return context
