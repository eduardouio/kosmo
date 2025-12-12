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
        
        invoice.order.status = "PENDIENTE"
        Invoice.order.is_invoiced = False
        Invoice.order.id_invoice = 0
        Invoice.order.num_invoice = None
        invoice.order.save()

        parent_order = Order.objects.filter(parent_order = invoice.order.id).first()
        parent_order.status = "PENDIENTE"
        parent_order.is_invoiced = False
        parent_order.id_invoice = 0
        parent_order.num_invoice = None
        parent_order.save()

        purchase_invoice = Invoice.objects.filter(order = parent_order.id).first()
        purchase_invoice.is_active = False
        purchase_invoice.status = "ANULADO"
        purchase_invoice.save()

        Invoice.disable_invoice_items(invoice)
        Invoice.disable_invoice_items(purchase_invoice)
        
        invoice.is_active = False
        invoice.status = "ANULADO"
        invoice.save()

        return (
            reverse("order_detail_presentation", kwargs={"pk": invoice.order.id})
            + "?action=deleted_related"
        )

