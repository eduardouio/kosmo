from django.views.generic import RedirectView
from common.AppLoger import loggin_event
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from partners.models import Partner, Bank, Contact, DAE
from trade.models import Order, Invoice


# socios/eliminar/<int:pk>/
class PartnerDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        loggin_event('Inicio de proceso de eliminación de socio', False)
        partner = Partner.objects.get(pk=kwargs['pk'])
        url_name = 'customers_list'
        if partner.type_partner == 'PROVEEDOR':
            url_name = 'supliers_list'

        has_orders = Order.objects.filter(
            partner=partner, is_active=True).exists()

        has_invoices = Invoice.objects.filter(
            partner=partner, is_active=True).exists()

        if has_orders or has_invoices:
            url = str(reverse_lazy('partner_detail',
                      kwargs={'pk': partner.pk}))
            return f'{url}?action=cannot_delete&reason=has_dependencies'

        partner.delete(partner.pk)

        url = str(reverse_lazy(url_name))
        return f'{url}?action=deleted'
