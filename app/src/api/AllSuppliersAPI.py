import json
from django.http import JsonResponse
from django.views import View
from partners.models import Partner


class AllSuppliersAPI(View):

    def get(self, request, *args, **kwargs):
        suppliers = Partner.get_suppliers()
        if not suppliers:
            return JsonResponse(
                {
                    'error': 'Suppliers not found'
                },
                status=404
            )

        result_dict = []

        for supplier in suppliers:
            item = {
                'id': supplier.id,
                'name': supplier.name,
                'business_tax_id': supplier.business_tax_id,
                'address': supplier.address,
                'city': supplier.city,
                'website': supplier.website,
                'credit_term': supplier.credit_term,
                'skype': supplier.skype,
                'email': supplier.email,
                'phone': supplier.phone,
                'is_active': supplier.is_active,
            }
            result_dict.append(item)

        return JsonResponse(result_dict, safe=False)