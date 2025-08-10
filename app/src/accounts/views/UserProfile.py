
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models.License import License
from common.AppLoger import loggin_event
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie


@method_decorator(ensure_csrf_cookie, name='dispatch')
class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'presentations/user_presentation.html'

    def get_context_data(self, **kwargs):
        loggin_event("Ingreso a perfil de usuario")
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        # Buscar la licencia activa o la más reciente del usuario
        license_obj = (
            License.objects.filter(user=user, is_active=True)
            .order_by('-activated_on', '-created_at')
            .first()
        )
        if not license_obj:
            license_obj = (
                License.objects.filter(user=user)
                .order_by('-activated_on', '-created_at')
                .first()
            )
        licencia_txt = 'sí' if license_obj else 'no'
        usuario_txt = getattr(user, 'email', str(user))
        loggin_event(
            f"Cargando perfil de {usuario_txt} | licencia={licencia_txt}"
        )
        ctx.update(
            {
                'title_page': 'Perfil de Usuario',
                'user_profile': user,
                'show_alert': False,
                'license': license_obj,
            }
        )
        return ctx
