from django.urls import path, reverse
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from trade.models import Invoice, Order


# trade/invoice/delete/<int:pk>/
class DeleteInvoiceView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        invoice_id = kwargs.get('pk')

        try:
            invoice = Invoice.objects.get(pk=invoice_id)

            # Verificar que la factura esté activa
            if not invoice.is_active:
                raise Http404("La factura no existe o ya ha sido eliminada")

            # Marcar la factura como inactiva
            invoice.is_active = False
            invoice.status = 'ANULADO'
            invoice.save()

            # Actualizar la orden relacionada
            order = invoice.order
            order.status = 'PENDIENTE'
            order.is_invoiced = False
            order.id_invoice = 0
            order.num_invoice = None
            order.save()

            # Redirigir a la vista de detalle de la orden
            return reverse('order_detail_presentation', kwargs={'pk': order.id}) + '?action=deleted_related'

        except Invoice.DoesNotExist:
            raise Http404("La factura no existe")
