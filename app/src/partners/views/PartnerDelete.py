import json
from django.urls import reverse_lazy
from partners.models import Partner
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner


class PartnerDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        partner = Partner.objects.get(pk=kwargs['pk'])
        try:
            partner.delete()
            url = reverse_lazy('partner_list')
            return f'{url}?action=deleted'
        except Exception as e:
            print(e)
            url = reverse_lazy('equipment_detail', kwargs={'pk': partner.pk})
            url = ''.join([url, '?action=no_delete'])
            return url
