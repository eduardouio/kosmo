from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from trade.models.Payment import Payment, METHOD_CHOICES
from common.InvoiceBalance import InvoiceBalance
from partners.models import Partner

import json
from decimal import Decimal


# pagos/nuevo/
class PaymentFormView(LoginRequiredMixin, View):
    template_name = 'forms/payment_form.html'

    def get(self, request):
        # Obtener todas las facturas pendientes con saldo recalculado
        # Solo facturas activas (is_active=True)
        invoices_data = InvoiceBalance.get_pending_invoices()
        
        context = {
            'method_choices': METHOD_CHOICES,
            'partners': Partner.objects.filter(is_active=True),  # Solo partners activos
            'invoices_data': invoices_data,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        data = request.POST

        try:
            # Crear nuevo pago
            payment = Payment()
            payment.created_by = request.user

            # Actualizar datos del pago
            payment.date = data.get('date')
            payment.amount = Decimal(data.get('amount', '0.0'))
            payment.method = data.get('method')
            payment.bank = data.get('bank')
            payment.nro_account = data.get('nro_account')
            payment.nro_operation = data.get('nro_operation')
            payment.observations = data.get('observations', '')
            payment.updated_by = request.user
            payment.is_active = True  # Asegurar que se crea como activo

            # Manejar archivo de documento si se proporciona
            if 'document' in request.FILES:
                payment.document = request.FILES['document']

            payment.save()

            # Procesar facturas asociadas al pago
            invoice_payments = json.loads(data.get('invoice_payments', '{}'))

            if invoice_payments:
                # Validar que todas las facturas estén activas
                valid_invoice_payments = {}
                for invoice_id, amount in invoice_payments.items():
                    try:
                        invoice = Invoice.objects.get(
                            id=invoice_id, 
                            is_active=True
                        )
                        if invoice.status != 'ANULADO':
                            valid_invoice_payments[invoice_id] = amount
                    except Invoice.DoesNotExist:
                        continue
                
                if valid_invoice_payments:
                    InvoiceBalance.apply_payment_to_invoices(
                        payment.id, valid_invoice_payments)

            messages.success(request, "Pago guardado correctamente")
            return redirect(reverse('payment_detail', kwargs={'pk': payment.id}))

        except Exception as e:
            messages.error(request, f"Error al guardar el pago: {str(e)}")
            return redirect(request.path)
