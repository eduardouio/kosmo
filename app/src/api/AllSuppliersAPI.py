from django.http import JsonResponse
from django.views import View
from partners.models import Partner, Contact
from products.models import StockDetail, StockDay


class AllSuppliersAPI(View):

    def get(self, request, *args, **kwargs):
        id_stock = request.GET.get('id_stock', None)
        stock_day = StockDay.get_by_id(id_stock)
        suppliers = Partner.get_suppliers()
        if not suppliers or not stock_day:
            return JsonResponse(
                {
                    'error': 'Proveedor o Stock no encontrado'
                },
                status=404
            )

        result_dict = []

        for supplier in suppliers:
            contact = Contact.get_principal_by_partner(supplier)
            contact_dict = {}
            if contact:
                contact_dict = {
                    'name': contact.name,
                    'position': contact.position,
                    'contact_type': contact.contact_type,
                    'phone': contact.phone,
                    'email': contact.email,
                    'is_principal': contact.is_principal
                }
            have_stock = len(StockDetail.get_stock_day_partner(
                stock_day, supplier)
            ) > 0
            item = {
                'id': supplier.id,
                'name': supplier.name,
                'short_name': supplier.short_name,
                'business_tax_id': supplier.business_tax_id,
                'address': supplier.address,
                'city': supplier.city,
                'website': supplier.website,
                'credit_term': supplier.credit_term,
                'is_profit_margin_included': supplier.is_profit_margin_included,
                'default_profit_margin': supplier.default_profit_margin,
                'consolidate': supplier.consolidate,
                'skype': supplier.skype,
                'email': supplier.email,
                'phone': supplier.phone,
                'is_active': supplier.is_active,
                'contact': contact_dict,
                'is_selected': False,
                'have_stock': have_stock,
            }
            result_dict.append(item)

        return JsonResponse(result_dict, safe=False)
