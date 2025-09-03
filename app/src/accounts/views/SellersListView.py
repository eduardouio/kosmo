from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.CustomUserModel import CustomUserModel
from common.AdminOnlyMixin import AdminOnlyMixin


class SellersListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
    model = CustomUserModel
    template_name = 'presentations/seller_list.html'
    context_object_name = 'sellers'

    def get_queryset(self):
        return (
            CustomUserModel.get_sellers()
            .order_by('first_name', 'last_name')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = 'Vendedores'
        action = self.request.GET.get('action')
        ctx['action'] = action
        message = ''
        if action == 'created':
            message = 'Vendedor creado correctamente.'
        elif action == 'updated':
            message = 'Vendedor actualizado.'
        ctx['message'] = message
        return ctx
