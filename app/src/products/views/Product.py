import json
from django.urls import reverse_lazy
from django import forms
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
    ListView,
    DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'image', 'variety', 'default_rend'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'maxlength': '255'}),
            'image': forms.ClearableFileInput(),
            'variety': forms.TextInput(attrs={'maxlength': '255'}),
            'default_rend': forms.NumberInput(attrs={'step': '0.01'}),
        }


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'forms/product-form.html'

    def get_context_data(self, *args, **kwargs):
        ctx = super(ProductCreateView, self).get_context_data(*args, **kwargs)
        ctx['title_bar'] = 'Create Product'
        return ctx

    def get_success_url(self):
        url = reverse_lazy('product-detail', kwargs={'pk': self.object.id})
        url += '?action=created'
        return url


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'forms/product-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = f'Actualizar Producto {self.object.name}'
        context['title_page'] = f'Actualizar Producto {self.object.name}'
        return context

    def get_success_url(self):
        url = reverse_lazy('product-detail', kwargs={'pk': self.object.pk})
        url = f'{url}?action=updated'
        return url


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'forms/product-confirm-delete.html'

    def get_success_url(self):
        url = reverse_lazy('product-list')
        return f'{url}?action=deleted'


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
        message = ''

        if context['action_type'] == 'created':
            message = 'El producto ha sido creado con éxito.'
        elif context['action_type'] == 'updated':
            message = 'El producto ha sido actualizado con éxito.'
        elif context['action_type'] == 'deleted':
            message = 'Producto eliminado correctamente.'
        elif context['action_type'] == 'no_delete':
            message = 'No es posible eliminar el producto. Existen dependencias.'

        context['message'] = message
        return context
