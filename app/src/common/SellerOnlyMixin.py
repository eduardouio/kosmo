from django.contrib.auth.mixins import UserPassesTestMixin


class SellerOnlyMixin(UserPassesTestMixin):
    """Restringe acceso solo a vendedores."""

    def test_func(self):
        user = self.request.user
        return (
            user.is_authenticated and
            getattr(user, 'roles', '') == 'VENDEDOR'
        )

    def handle_no_permission(self):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("No autorizado")
