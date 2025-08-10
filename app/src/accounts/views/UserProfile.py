
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/user_profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx.update(
            {
                'title_page': 'Perfil de Usuario',
                'user_profile': user,
                'show_alert': False,
            }
        )
        return ctx
