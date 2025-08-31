from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from accounts.models.CustomUserModel import CustomUserModel


class AdminOnlyMixin(UserPassesTestMixin):
	"""Restringe acceso solo a administradores."""

	def test_func(self):
		user = self.request.user
		return (
			user.is_authenticated and
			getattr(user, 'roles', '') == 'ADMINISTRADOR'
		)

	def handle_no_permission(self):
		from django.core.exceptions import PermissionDenied
		raise PermissionDenied("No autorizado")


class SellersListView(LoginRequiredMixin, AdminOnlyMixin, ListView):
	model = CustomUserModel
	template_name = 'presentations/seller_list.html'
	context_object_name = 'sellers'

	def get_queryset(self):
		return CustomUserModel.get_sellers().order_by('first_name', 'last_name')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['title_page'] = 'Vendedores'
		return ctx


class SellerDetailView(LoginRequiredMixin, AdminOnlyMixin, DetailView):
	model = CustomUserModel
	template_name = 'presentations/seller_detail.html'
	context_object_name = 'object'

	def get_queryset(self):
		# Limita a vendedores
		return CustomUserModel.get_sellers()

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		seller = self.object
		ctx['title_page'] = (
			f"Vendedor {seller.first_name} {seller.last_name}".strip()
		)
		return ctx
