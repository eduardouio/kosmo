from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from partners.models import Contact, Partner
from django import forms


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'partner', 'name', 'position', 'phone', 'email', 'is_principal', 'is_active', 'notes', 'contact_type'
        ]
        widgets = {
            'partner': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'name': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'position': forms.TextInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'phone': forms.TextInput(attrs={'maxlength': '20', 'class': 'form-control form-control-sm'}),
            'email': forms.EmailInput(attrs={'maxlength': '255', 'class': 'form-control form-control-sm'}),
            'contact_type': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'is_principal': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-sm', 'rows': 3}),
        }


# contactos/nuevo/<int:id_partner>/
class ContactCreateView(LoginRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = 'forms/contact_form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ContactCreateView, self).get_context_data(*args, **kwargs)
        ctx['id_partner'] = self.kwargs.get('id_partner')
        ctx['title_section'] = 'Registrar Nuevo Contacto'
        return ctx

    def get_form(self, form_class=None):
        form = super(ContactCreateView, self).get_form(form_class)
        id_partner = self.kwargs.get('id_partner')
        if id_partner:
            partner = Partner.objects.get(pk=id_partner)
            if id_partner:
                form.fields['partner'].initial = partner
        return form

    def get_success_url(self):
        url = reverse_lazy('contact_detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


# contactos/actualizar/<int:pk>/
class ContactUpdateView(LoginRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = 'forms/contact_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Actualizar Contacto {}'.format(
            self.object.name)
        context['title_page'] = 'Actualizar Contacto {}'.format(
            self.object.name)
        context['action'] = None
        context['id_partner'] = self.object.pk
        return context

    def get_success_url(self):
        url = reverse_lazy('contact_detail', kwargs={'pk': self.object.pk})
        url = '{url}?action=updated'.format(url=url)
        return url


# contactos/eliminar/<int:pk>/
class ContactDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        contact = Contact.objects.get(pk=kwargs['pk'])
        partner = contact.partner
        try:
            contact.delete()
            url = reverse_lazy('partner_detail', kwargs={'pk': partner.pk})
            return url + '?action=deleted_related'
        except Exception:
            url = reverse_lazy('contact_detail', kwargs={'pk': contact.pk})
            return url + '?action=no_delete_related'


# contactos/
class ContactListView(LoginRequiredMixin, ListView):
    model = Contact
    template_name = 'lists/contact_list.html'
    context_object_name = 'contacts'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super(ContactListView, self).get_context_data(**kwargs)
        context['title_section'] = 'Contactos'
        context['title_page'] = 'Listado de Contactos'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Contacto Eliminado Exitosamente'
        return context


# contactos/<int:pk>/
class ContactDetailView(LoginRequiredMixin, DetailView):
    model = Contact
    template_name = 'presentations/contact_presentation.html'
    context_object_name = 'contact'

    def get_context_data(self, **kwargs):
        context = super(ContactDetailView, self).get_context_data(**kwargs)
        context['title_section'] = self.object.name
        context['title_page'] = self.object.name
        context['action'] = self.request.GET.get('action')

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        message = ''

        if context['action'] == 'created':
            message = 'El contacto ha sido creado con éxito.'
        elif context['action'] == 'updated':
            message = 'El contacto ha sido actualizado con éxito.'
        elif context['action'] == 'no_delete':
            message = 'No se puede eliminar el registro. Existen dependencias'
        elif context['action'] == 'delete':
            message = 'Esta acción es irreversible. ¿Desea continuar?.'

        context['message'] = message
        return context
