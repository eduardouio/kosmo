from django.http import JsonResponse
from django.views import View
from partners.models import Partner, Contact


class AllCustomerAPI(View):

    def get(self, request, *args, **kwargs):
        all_cutomers = Partner.get_customers()

        suppliers_dict = []

        for supplier in all_cutomers:
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
                'is_selected': False,
            }
            suppliers_dict.append(item)

        return JsonResponse(suppliers_dict, safe=False)