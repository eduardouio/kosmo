from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from accounts.models import CustomUserModel


# /
class HomeTV(LoginRequiredMixin, TemplateView):
    template_name = 'pages/home.html'

    def get(self, request, *args, **kwargs):
        page_data = {
            'title_page': 'Inicio',
            'module_name': 'Accounts',
            'message': '',
            'status': 'logged_in',
        }
        context = self.get_context_data(**kwargs)
        return self.render_to_response({**context, **page_data})