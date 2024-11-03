from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from partners.models import Partner, DAE


class DAEForm(forms.ModelForm):
    class Meta:
        model = DAE
        fields = ['partner', 'dae', 'date_begin',
                  'date_end', 'is_active', 'notes']
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'dae': forms.TextInput(attrs={'maxlength': '50', 'class': 'form-control form-control-sm'}),
            'date_begin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'date_end': forms.DateInput(attrs={'type': 'date', 'class': 'form-control form-control-sm'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


class DAECreateView(LoginRequiredMixin, CreateView):
    model = DAE
    form_class = DAEForm
    template_name = 'forms/dae_form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['id_partner'] = self.kwargs.get('id_partner')
        ctx['title_section'] = 'Registrar Nuevo DAE'
        return ctx

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        id_partner = self.kwargs.get('id_partner')
        if id_partner:
            partner = Partner.objects.get(pk=id_partner)
            form.fields['partner'].initial = partner
        return form

    def get_success_url(self):
        url = reverse_lazy('dae_detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


class DAEUpdateView(LoginRequiredMixin, UpdateView):
    model = DAE
    form_class = DAEForm
    template_name = 'forms/dae_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = f'Actualizar DAE {self.object.dae}'
        context['title_page'] = f'Actualizar DAE {self.object.dae}'
        context['action'] = None
        context['id_partner'] = self.object.partner.pk
        return context

    def get_success_url(self):
        url = reverse_lazy('dae_detail', kwargs={'pk': self.object.pk})
        url += '?action=updated'
        return url


class DAEDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        dae = DAE.objects.get(pk=kwargs['pk'])
        partner = dae.partner
        try:
            dae.delete()
            url = reverse_lazy('partner_detail', kwargs={'pk': partner.pk})
            return url + '?action=deleted_related'
        except Exception:
            url = reverse_lazy('dae_detail', kwargs={'pk': dae.pk})
            return url + '?action=no_delete_related'


class DAEListView(LoginRequiredMixin, ListView):
    model = DAE
    template_name = 'lists/dae_list.html'
    context_object_name = 'daes'
    ordering = ['dae']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'DAEs'
        context['title_page'] = 'Listado de DAEs'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'DAE Eliminado Exitosamente'
        return context


class DAEDetailView(LoginRequiredMixin, DetailView):
    model = DAE
    template_name = 'presentations/dae_presentation.html'
    context_object_name = 'dae'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = self.object.dae
        context['title_page'] = self.object.dae
        context['action'] = self.request.GET.get('action')

        if 'action' in self.request.GET:
            context['action_type'] = self.request.GET.get('action')
            if context['action'] == 'created':
                context['message'] = 'El DAE ha sido creado con éxito.'
            elif context['action'] == 'updated':
                context['message'] = 'El DAE ha sido actualizado con éxito.'
            elif context['action'] == 'no_delete':
                context['message'] = 'No se puede eliminar el registro. Existen dependencias'
            elif context['action'] == 'delete':
                context['message'] = 'Esta acción es irreversible. ¿Desea continuar?.'

        return context
