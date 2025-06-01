from partners.models import Partner
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Partner


class PartnerAutoRegisterList(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'lists/partner_list.html'
    context_object_name = 'partners'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super(PartnerAutoRegisterList, self).get_context_data(**kwargs)
        context['title_section'] = 'Socios de Negocio'
        context['title_page'] = 'Socios Sin Confirmar'
        context['action'] = None
        context['source_page'] = self.request.path.split('/')[2]

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Socio Eliminado Exitosamente'
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            is_active=True,
            is_verified=False,
        )
