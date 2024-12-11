from django.urls import reverse_lazy
from django.views.generic import (
    RedirectView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product


class ProductDeleteView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        product = Product.objects.get(pk=kwargs['pk'])
        try:
            product.delete()
            url = reverse_lazy('product_list') + '?action=deleted'
            return url
        except Exception as e:
            print(e)
            url = reverse_lazy('product_detail', kwargs={'pk': product.pk})
            return url + '?action=no_delete'
