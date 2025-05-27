from django.http import JsonResponse
from django.views import View
from partners.models import Partner, Contact
from products.models import StockDetail, StockDay
from common.AppLoger import loggin_event


class AllSuppliersAPI(View):

    def get(self, request, *args, **kwargs):
        loggin_event('Obteniendo todos los proveedores')

        id_stock = request.GET.get('id_stock', None)
        if id_stock is None:
            return JsonResponse({'error': 'ID de stock no proporcionado'}, status=400)

        suppliers = Partner.get_suppliers()

        if not suppliers:
            return JsonResponse({'error': 'No se encontraron proveedores'}, status=404)

        include_stock = id_stock != '0'
        if include_stock:
            stock_day = StockDay.get_by_id(id_stock) if include_stock else None

        result_dict = []

        for supplier in suppliers:
            related_customers = [
                {
                    'id': c.id,
                    'name': c.name,
                    'business_tax_id': c.business_tax_id,
                    'country': c.country,
                    'city': c.city,
                    'website': c.website,
                    'credit_term': c.credit_term,
                    'consolidate': c.consolidate,
                    'skype': c.skype,
                    'email': c.email,
                    'phone': c.phone,
                    'is_active': c.is_active,
                }
                for c in supplier.partner.all() if c.is_active
            ]

            contact = Contact.get_principal_by_partner(supplier)
            contact_dict = {
                'name': contact.name,
                'position': contact.position,
                'contact_type': contact.contact_type,
                'phone': contact.phone,
                'email': contact.email,
                'is_principal': contact.is_principal
            } if contact else {}

            have_stock = False
            if include_stock:
                have_stock = len(StockDetail.get_stock_day_partner(
                    stock_day, supplier)) > 0

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
                'related_partners': related_customers
            }
            result_dict.append(item)

        loggin_event('Proveedores obtenidos')
        return JsonResponse(result_dict, safe=False)
