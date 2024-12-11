from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


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

    def get_object(self):
        '''Access the object and split the colors'''
        object = super().get_object()
        object.colors = object.colors.split(',')
        return object
