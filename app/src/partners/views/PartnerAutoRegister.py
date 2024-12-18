from django.views.generic import TemplateView


class PartnerAutoRegister(TemplateView):
    template_name = 'forms/auto_register.html'

    def get_context_data(self, **kwargs):
        type_partner = self.request.GET.get('type')
        context = super().get_context_data(**kwargs)
        context['type_partner'] = 'CLIENTE' if type_partner == 'client' else 'PROVEEDOR'
        return context
    
