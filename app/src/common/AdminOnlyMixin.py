from django.contrib.auth.mixins import UserPassesTestMixin


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

