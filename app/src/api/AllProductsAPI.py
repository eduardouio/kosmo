from django.views import View
from products.models import Product
from django.http import JsonResponse


class AllProductsAPI(View):
    def get(self, request, *args, **kwargs):
        products = Product.get_all()
        products_list = []
        for product in products:
            product_image = product.image.url if product.image else ''
            products_list.append({
                "id": product.id,
                "name": product.name,
                "variety": product.variety,
                "image": product_image,
                "colors": product.colors,
                "default_profit_margin": product.default_profit_margin
            })

        return JsonResponse(
            {'products': products_list},
            safe=False,
            status=200
        )
