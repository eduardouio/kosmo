from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from accounts.models.License import License
from common.AppLoger import loggin_event


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

        # Unificar en un solo JSON serializable
        def to_iso(dt):
            return dt.isoformat() if dt else None

        license_json = None
        if license_obj:
            license_json = {
                'id': license_obj.id,
                'license_key': license_obj.license_key,
                'activated_on': to_iso(license_obj.activated_on),
                'expires_on': to_iso(license_obj.expires_on),
                'enterprise': license_obj.enterprise,
                'url_server': license_obj.url_server,
                'is_active': getattr(license_obj, 'is_active', None),
                # Campos BaseModel de licencia
                'notes': getattr(license_obj, 'notes', None),
                'created_at': to_iso(getattr(license_obj, 'created_at', None)),
                'updated_at': to_iso(getattr(license_obj, 'updated_at', None)),
            }

        userProfile = {
            'id': user.id,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'email': user.email or '',
            'phone': getattr(user, 'phone', '') or '',
            'notes': getattr(user, 'notes', '') or '',
            'roles': getattr(user, 'roles', ''),
            # Metadatos de usuario
            'is_active': getattr(user, 'is_active', True),
            'is_confirmed_mail': getattr(user, 'is_confirmed_mail', False),
            'last_login': to_iso(getattr(user, 'last_login', None)),
            'date_joined': to_iso(getattr(user, 'date_joined', None)),
            'picture_url': user.picture.url if getattr(user, 'picture', None) else None,
            # Licencia
            'has_license': bool(license_obj),
            'license': license_json,
        }

        ctx.update(
            {
                'title_page': 'Perfil de Usuario',
                'user_profile': user,
                'show_alert': False,
                'license': license_obj,
                'user_profile_json': userProfile
            }
        )
        return ctx
