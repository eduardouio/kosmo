import json
from django.urls import reverse_lazy
from partners.models import Partner
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin


class PartnerDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        partner = Partner.objects.get(pk=kwargs['pk'])
        try:
            partner.delete(partner.pk)  # Pasar el ID como parámetro requerido
            url = str(reverse_lazy('partner_list'))  # Convertir a string
            return f'{url}?action=deleted'
        except Exception as e:
            print(e)
            url = str(reverse_lazy('partner_detail', kwargs={'pk': partner.pk}))  # Corregir nombre de URL y convertir a string
            return f'{url}?action=no_delete'
