from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


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
