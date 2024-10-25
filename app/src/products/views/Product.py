import json
from django.urls import reverse_lazy
from django import forms
from django.http import HttpResponseRedirect
from django.views.generic import (
    CreateView,
    UpdateView,
    RedirectView,
    ListView,
    DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'image', 'variety', 'default_rend', 'notes'
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


class ProductDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])
        try:
            product.delete()
            url = reverse_lazy('product_list') + '?action=deleted'
            return url
        except Exception as e:
            url = reverse_lazy('product_detail', kwargs={'pk': product.pk})
            return url + '?action=no_delete'


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'lists/product_list.html'
    context_object_name = 'products'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['title_section'] = 'Productos'
        context['title_page'] = 'Listado de Productos'
        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['action'] = 'deleted'
            context['message'] = 'Producto Eliminado Exitosamente'
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'presentations/product_presentation.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)
        context['title_section'] = self.object.name
        context['title_page'] = self.object.name

        if 'action' not in self.request.GET:
            return context

        context['action_type'] = self.request.GET.get('action')
        context['action'] = self.request.GET.get('action')
        message = ''

        if context['action_type'] == 'created':
            message = 'El producto ha sido creado con éxito.'
        elif context['action_type'] == 'updated':
            message = 'El producto ha sido actualizado con éxito.'
        elif context['action_type'] == 'delete':
            message = '¿Esta seguro que desea eliminar el producto?, esta acción no se puede deshacer.'
        elif context['action_type'] == 'no_delete':
            message = 'No es posible eliminar el producto. Existen dependencias.'

        context['message'] = message
        return context
