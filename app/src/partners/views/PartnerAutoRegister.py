from django.views.generic import TemplateView
from django.shortcuts import redirect, render
from django.contrib import messages
from partners.models import Partner, Contact, Bank


# socios/auto-registro/
class PartnerAutoRegister(TemplateView):
    template_name = 'forms/auto_register.html'

    def get_context_data(self, **kwargs):
        type_partner = self.request.GET.get('type')
        context = super().get_context_data(**kwargs)
        context['type_partner'] = 'CLIENTE' if type_partner == 'client' else 'PROVEEDOR'
        return context

    def post(self, request, *args, **kwargs):
        try:
            # Procesamos los campos numéricos para manejar cadenas vacías
            dispatch_days = request.POST.get('dispatch_days')
            dispatch_days = int(dispatch_days) if dispatch_days and dispatch_days.strip() else None

            credit_term = request.POST.get('credit_term')
            credit_term = int(credit_term) if credit_term and credit_term.strip() else 0

            partner_data = {
                'name': request.POST.get('name'),
                'city': request.POST.get('city'),
                'country': request.POST.get('country'),
                'address': request.POST.get('address'),
                'area_code': request.POST.get('area_code'),
                'skype': request.POST.get('skype'),
                'website': request.POST.get('website'),
                'business_tax_id': request.POST.get('business_tax_id'),
                'credit_term': credit_term,  # Valor procesado
                'consolidate': request.POST.get('consolidated') == 'on',
                'dispatch_days': dispatch_days,  # Valor procesado
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
                'status': 'PENDIENTE',
                'is_verified': False,
            }

            # Procesamos los años en el negocio
            businnes_start_str = request.POST.get('businnes_start')
            if businnes_start_str and businnes_start_str.strip():
                try:
                    years = int(businnes_start_str)
                    partner_data['years_in_market'] = years
                except ValueError:
                    # Si hay error de conversión, lo dejamos como None,
                    # el modelo se encargará del valor por defecto.
                    partner_data['years_in_market'] = None
            else:
                partner_data['years_in_market'] = None

            # Filtramos los valores None para permitir los valores por defecto de la base de datos
            filtered_data = {k: v for k, v in partner_data.items() if v is not None}
            partner = Partner.objects.create(**filtered_data)

            contacts_data = [
                {
                    'name': request.POST.get('contact_manager'),
                    'email': request.POST.get('email_manager'),
                    'contact_type': 'GERENCIA',
                    'is_principal': True
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
                if contact_data.get('name'):
                    Contact.objects.create(
                        partner=partner,
                        **{k: v for k, v in contact_data.items() if v is not None}
                    )

            messages.success(
                request, 'Registro creado exitosamente. Su solicitud será revisada por nuestro equipo.')

            return render(request, 'presentations/success_register_partner.html', {
                'partner': partner,
                'type_partner': partner.type_partner
            })

        except Exception as e:
            messages.error(request, f'Error al crear el registro: {str(e)}')
            return self.get(request, *args, **kwargs)