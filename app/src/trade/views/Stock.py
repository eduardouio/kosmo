from datetime import date
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from products.models import StockDay


class StockDayForm(forms.ModelForm):
    class Meta:
        model = StockDay
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'text', 'class': 'form-control form-control-sm', 'readonly': 'readonly'}),
        }


class StockDayCreateView(LoginRequiredMixin, CreateView):
    model = StockDay
    form_class = StockDayForm
    template_name = 'forms/stockday_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['date'].initial = date.today()
        return form

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx['title_section'] = 'Registrar Nueva Disponibilidad de Stock Diario'
        return ctx

    def get_success_url(self):
        all_stock_days = StockDay.objects.all().exclude(pk=self.object.id)
        [StockDay.disable(i) for i in all_stock_days]
        url = reverse_lazy('stock_detail_detail', kwargs={'pk': self.object.id})
        return url + '#/import/'


class StockDayDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        stock_day = StockDay.objects.get(pk=kwargs['pk'])
        try:
            stock_day.delete()
            url = reverse_lazy('stock_list')
            return url + '?action=deleted'
        except Exception:
            url = reverse_lazy('stock_detail', kwargs={'pk': stock_day.pk})
            return url + '?action=no_delete'


class StockDayListView(LoginRequiredMixin, ListView):
    model = StockDay
    template_name = 'lists/stockday_list.html'
    context_object_name = 'stock_days'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Stock Diario'
        context['title_page'] = 'Listado de Stock Diario'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Stock Diario Eliminado Exitosamente'
        return context


class StockDayDetailView(LoginRequiredMixin, DetailView):
    model = StockDay
    template_name = 'presentations/stockday_presentation.html'
    context_object_name = 'stock_day'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Detalle de Stock Diario {}'.format(self.object.date)
        context['action'] = self.request.GET.get('action')

        if 'action' in self.request.GET:
            context['action_type'] = self.request.GET.get('action')
            if context['action'] == 'created':
                context['message'] = 'Stock Diario Creado Exitosamente'
            if context['action'] == 'no_delete':
                context['message'] = 'No se puede eliminar el registro. Existen dependencias'
            elif context['action'] == 'delete':
                context['message'] = 'Esta acción es irreversible. ¿Desea continuar?.'

        return context
