from django.urls import reverse_lazy
from django import forms
from django.views.generic import (
    CreateView,
    UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'image', 'variety', 'default_rend', 'notes', 'colors'
        ]
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'maxlength': '255',
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Nombre',
                    'required': 'required'
                }
            ),
            'image': forms.ClearableFileInput(),
            'colors': forms.TextInput(
                attrs={
                    'maxlength': '255',
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Colores',
                }
            ),
            'variety': forms.TextInput(
                attrs={
                    'maxlength': '255',
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Variedad',
                    'required': 'required'
                }
            ),
            'default_rend': forms.NumberInput(
                attrs={
                    'step': '0.01',
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Rendimiento por defecto',
                    'required': 'required'
                }
            ),
            'notes': forms.Textarea(
                attrs={
                    'class': 'form-control form-control-sm',
                    'placeholder': 'Notas',
                    'rows': '3'
                }
            ),
        }


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'forms/product_form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductCreateView, self).get_context_data(*args, **kwargs)
        ctx['title_bar'] = 'Create Product'
        return ctx

    def get_success_url(self):
        url = reverse_lazy('product_detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'forms/product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = f'Actualizar Producto {self.object.name}'
        context['title_page'] = f'Actualizar Producto {self.object.name}'
        return context

    def get_success_url(self):
        url = reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
        url = '{url}?action=updated'.format(url=url)
        return url
