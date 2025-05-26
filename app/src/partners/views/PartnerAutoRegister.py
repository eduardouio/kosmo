from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from ..models import Partner, Contact


class PartnerAutoRegister(TemplateView):
    template_name = 'forms/auto_register.html'

    def get_context_data(self, **kwargs):
        type_partner = self.request.GET.get('type')
        context = super().get_context_data(**kwargs)
        context['type_partner'] = 'CLIENTE' if type_partner == 'client' else 'PROVEEDOR'
        return context

    def post(self, request, *args, **kwargs):
        try:
            # Crear Partner
            partner_data = {
                'name': request.POST.get('name'),
                'city': request.POST.get('city'),
                'country': request.POST.get('country'),
                'address': request.POST.get('address'),
                'area_code': request.POST.get('area_code'),
                'skype': request.POST.get('skype'),
                'website': request.POST.get('website'),
                'business_tax_id': request.POST.get('business_tax_id'),
                'businnes_start': request.POST.get('businnes_start'),
                'consolidate': request.POST.get('consolidated') == 'on',
                'dispatch_days': request.POST.get('dispatch_days'),
                'cargo_reference': request.POST.get('cargo_reference'),
                'reference_1': request.POST.get('reference_1'),
                'contact_reference_1': request.POST.get('contact_reference_1'),
                'phone_reference_1': request.POST.get('phone_reference_1'),
                'reference_2': request.POST.get('reference_2'),
                'contact_reference_2': request.POST.get('contact_reference_2'),
                'phone_reference_2': request.POST.get('phone_reference_2'),
                'type_partner': 'CLIENTE' if request.POST.get('tipo_socio') == '2' else 'PROVEEDOR',
                'phone': request.POST.get('contact_phone'),
                'email_payment': request.POST.get('email_payment'),
            }

            partner = Partner.objects.create(
                **{k: v for k, v in partner_data.items() if v})

            # Crear contactos
            contacts_data = [
                {
                    'name': request.POST.get('contact_manager'),
                    'email': request.POST.get('email_manager'),
                    'contact_type': 'GERENCIA'
                },
                {
                    'name': request.POST.get('contact_sales'),
                    'email': request.POST.get('email_sales'),
                    'contact_type': 'COMERCIAL'
                },
                {
                    'name': request.POST.get('contact_payment'),
                    'email': request.POST.get('email_payment'),
                    'contact_type': 'FINANCIERO'
                },
                {
                    'name': request.POST.get('contact'),
                    'phone': request.POST.get('contact_phone'),
                    'contact_type': 'OTRO'
                }
            ]

            for contact_data in contacts_data:
                if contact_data['name']:
                    Contact.objects.create(
                        partner=partner,
                        **{k: v for k, v in contact_data.items() if v and k != 'name'},
                        name=contact_data['name']
                    )

            messages.success(request, 'Registro creado exitosamente')
            return redirect('partner_detail', pk=partner.pk)

        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')
            return self.get(request, *args, **kwargs)
