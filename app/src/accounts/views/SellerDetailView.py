from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models.CustomUserModel import CustomUserModel
from common.AdminOnlyMixin import AdminOnlyMixin


class SellerDetailView(LoginRequiredMixin, AdminOnlyMixin, DetailView):
    model = CustomUserModel
    template_name = 'presentations/seller_detail.html'
    context_object_name = 'object'

    def get_queryset(self):
        return CustomUserModel.get_sellers()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        seller = self.object
        ctx['title_page'] = (
            f"Vendedor {seller.first_name} {seller.last_name}".strip()
        )
        return ctx
