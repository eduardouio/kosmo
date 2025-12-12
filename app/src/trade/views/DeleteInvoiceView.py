from django.urls import reverse
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from trade.models import Invoice
from common.AppLoger import loggin_event
from trade.models.Order import Order


class DeleteInvoiceView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        loggin_event(
            self.request.user,
            "DELETE_INVOICE",
            f"El usuario {self.request.user.username} ha eliminado la factura con ID {kwargs.get('pk')}",
        )

        invoice_id = kwargs.get("pk")
        invoice = Invoice.objects.get(pk=invoice_id)

        if not invoice.is_active:
            raise Http404("La factura no existe o ya ha sido eliminada")
        
        # Actualizar orden de venta
        invoice.order.status = "PENDIENTE"
        invoice.order.is_invoiced = False
        invoice.order.id_invoice = None
        invoice.order.num_invoice = None
        invoice.order.save()

        # Buscar y actualizar orden de compra relacionada
        parent_order = Order.objects.filter(parent_order=invoice.order.id).first()
        if parent_order:
            parent_order.status = "PENDIENTE"
            parent_order.is_invoiced = False    
            parent_order.id_invoice = None
            parent_order.num_invoice = None
            parent_order.save()

            # Anular factura de compra relacionada
            purchase_invoice = Invoice.objects.filter(order=parent_order.id).first()
            if purchase_invoice:
                purchase_invoice.is_active = False
                purchase_invoice.status = "ANULADO"
                purchase_invoice.save()
                Invoice.disable_invoice_items(purchase_invoice)

        # Desactivar items de la factura de venta
        Invoice.disable_invoice_items(invoice)
        
        # Anular factura de venta
        invoice.is_active = False
        invoice.status = "ANULADO"
        invoice.save()
        
        return (
            reverse("order_detail_presentation", kwargs={"pk": invoice.order.id})
            + "?action=deleted_related"
        )

