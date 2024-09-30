from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from accounts.models import CustomUserModel


# /accounts/login/
class LoginTV(TemplateView):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        page_data = {
            'title_page': 'Inicio Sesion',
            'module_name': 'Accounts',
            'message': '',
            'satus': 'not_logged_in',
        }
        if request.user.is_authenticated:
            page_data['status'] = 'logged_in'
            page_data['message'] = 'Ya has iniciado sesion'
            return HttpResponseRedirect('/')

        context = self.get_context_data(**kwargs)
        return self.render_to_response({**context, **page_data})

    def post(self, request, *args, **kwargs):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            page_data = {
                'title_page': 'Inicio Sesion',
                'module_name': 'Accounts',
                'message': 'Usuario o contraseña incorrecta',
                'status': 'not_logged_in',
            }
            context = self.get_context_data(**kwargs)
            return self.render_to_response({**context, **page_data})