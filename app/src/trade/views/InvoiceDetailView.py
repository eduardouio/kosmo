from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'presentations/invoice_presentation.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super(InvoiceDetailView, self).get_context_data(**kwargs)
        context['title_section'] = f"Factura {self.object.num_invoice}"
        context['title_page'] = f"Factura {self.object.num_invoice}"
        context['invoice_items'] = InvoiceItems.get_invoice_items(self.object)
        context['box_items'] = InvoiceBoxItems.objects.filter(
            invoice_item__invoice=self.object, is_active=True
        )
        context['awb'] = self.object.awb
        context['hawb'] = self.object.hawb  # Agregar HAWB al contexto
        context['dae_export'] = self.object.dae_export  # Agregar DAE Exportación al contexto
        context['cargo_agency'] = self.object.cargo_agency  # Agregar Agencia de Carga al contexto
        context['delivery_date'] = self.object.delivery_date  # Agregar Fecha de Entrega al contexto
        context['weight'] = self.object.weight  # Agregar Peso al contexto
        context['action'] = self.request.GET.get('action')

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

        context['message'] = message
        return context
