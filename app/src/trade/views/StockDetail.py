from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django import forms

from products.models import StockDay, StockDetail, BoxItems


class StockDetailForm(forms.ModelForm):
    class Meta:
        model = StockDetail
        fields = [
            'partner', 'box_model', 'tot_stem_flower', 'tot_cost_price_box'
        ]
        widgets = {
            'partner': forms.Select(
                attrs={'class': 'form-control form-control-sm',
                       'required': 'required', 'readonly': 'readonly'}
            ),
            'box_model': forms.Select(
                attrs={'class': 'form-control form-control-sm',
                       'required': 'required'}
            ),
            'tot_stem_flower': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm',
                       'placeholder': 'Cantidad de tallos', 'readonly': 'readonly'}
            ),
            'tot_cost_price_box': forms.NumberInput(
                attrs={'class': 'form-control form-control-sm',
                       'placeholder': 'Precio de costo por tallo'}
            ),
        }


class DetailStockDetail(LoginRequiredMixin, TemplateView):
    template_name = 'presentations/stock_detail_presentation.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_day = StockDay.get_by_id(kwargs['pk'])
        context['stock_day'] = stock_day
        context['stock_id'] = stock_day.id
        context['title_page'] = 'Diponibilidad {}'.format(
            stock_day.date.strftime('%d/%m/%Y')
        )
        return context


class SingleStockDetailCreateView(LoginRequiredMixin, CreateView):
    model = StockDetail
    form_class = StockDetailForm
    template_name = 'forms/stockdetail_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_bar'] = 'Crear StockDetail'
        return context

    def get_success_url(self):
        return reverse_lazy('stockdetail_detail', kwargs={'pk': self.object.pk}) + '?action=created'


class SingleStockDetailUpdateView(LoginRequiredMixin, UpdateView):
    model = StockDetail
    form_class = StockDetailForm
    template_name = 'forms/stock_item_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_page'] = 'Actualizar {}'.format(
            self.object.id
        )
        context['title_section'] = 'Actualizar Item #{} del {}'.format(
            self.object.id, self.object.stock_day.date.strftime('%d/%m/%Y')
        )
        context['stock_day'] = self.object.stock_day
        context['box_items'] = BoxItems.get_box_items(self.object)

        return context

    def get_success_url(self):
        url = reverse_lazy('stock_detail_detail',
                           kwargs={'pk': self.object.pk})
        url = '{url}?action=updated'.format(url=url)
        return url
