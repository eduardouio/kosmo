from django.http import JsonResponse
from django.views import View
from partners.models import Partner, Contact
from common.AppLoger import loggin_event


class AllCustomerAPI(View):

    def get(self, request, *args, **kwargs):
        loggin_event('Obteniendo todos los clientes')
        all_cutomers = Partner.get_customers()
        suppliers_dict = []

        for supplier in all_cutomers:
            contact = Contact.get_principal_by_partner(supplier)
            related_customers = supplier.partner.all()
            related_customers = [{
                'id': c.id,
                'name': c.name,
                'short_name': c.short_name,
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
            } for c in related_customers if c.is_active]
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

            item = {
                'id': supplier.id,
                'name': supplier.name,
                'business_tax_id': supplier.business_tax_id,
                'address': supplier.address,
                'country': supplier.country,
                'city': supplier.city,
                'website': supplier.website,
                'credit_term': supplier.credit_term,
                'consolidate': supplier.consolidate,
                'skype': supplier.skype,
                'email': supplier.email,
                'phone': supplier.phone,
                'is_active': supplier.is_active,
                'contact': contact_dict,
                'related_partners': related_customers,
                'is_selected': False,
            }
            suppliers_dict.append(item)

        loggin_event('Clientes obtenidos')
        return JsonResponse(suppliers_dict, safe=False)