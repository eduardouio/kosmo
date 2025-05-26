from django.http import JsonResponse
from django.views import View
from accounts.models import CustomUserModel


class SellersListAPI(View):
    """
    API para obtener la lista de vendedores registrados en el sistema.
    Devuelve un JSON con la información básica de cada vendedor.
    """

    def get(self, request, *args, **kwargs):
        sellers = CustomUserModel.get_sellers()

        sellers_data = []
        for seller in sellers:
            sellers_data.append({
                'id': seller.id,
                'name': seller.get_full_name() if seller.get_full_name() else seller.email,
                'email': seller.email,
                'phone': seller.phone or '',
                'is_active': seller.is_active
            })

        return JsonResponse({
            'status': 'success',
            'count': len(sellers_data),
            'sellers': sellers_data
        })
