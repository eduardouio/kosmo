from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from trade.models.Payment import Payment, METHOD_CHOICES
from trade.models.Invoice import Invoice
from common.SaleInvoices import InvoiceBalance
from partners.models import Partner

import json
from decimal import Decimal


class PaymentFormView(LoginRequiredMixin, View):
    template_name = 'forms/payment_form.html'

    def get(self, request, payment_id=None):
        context = {
            'method_choices': METHOD_CHOICES,
            'partners': Partner.objects.filter(is_active=True)
        }

        if payment_id:
            payment = get_object_or_404(Payment, id=payment_id)
            context['payment'] = payment

            # Obtener las facturas asociadas a este pago
            invoices_in_payment = payment.invoices.all()
            context['invoices_in_payment'] = invoices_in_payment

        return render(request, self.template_name, context)

    def post(self, request, payment_id=None):
        data = request.POST

        try:
            # Crear o actualizar pago
            if payment_id:
                payment = get_object_or_404(Payment, id=payment_id)
                payment.invoices.clear()  # Eliminar asociaciones anteriores
            else:
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

            # Manejar archivo de documento si se proporciona
            if 'document' in request.FILES:
                payment.document = request.FILES['document']

            payment.save()

            # Procesar facturas asociadas al pago
            invoice_payments = json.loads(data.get('invoice_payments', '{}'))

            if invoice_payments:
                InvoiceBalance.apply_payment_to_invoices(
                    payment.id, invoice_payments)

            messages.success(request, "Pago guardado correctamente")
            return redirect(reverse('payment_detail', kwargs={'payment_id': payment.id}))

        except Exception as e:
            messages.error(request, f"Error al guardar el pago: {str(e)}")
            return redirect(request.path)


class PaymentApiView(View):
    def get(self, request):
        action = request.GET.get('action')

        if action == 'get_partner_invoices':
            partner_id = request.GET.get('partner_id')
            pending_invoices = InvoiceBalance.get_pending_invoices(partner_id)

            invoices_data = []
            for invoice_data in pending_invoices:
                invoice = invoice_data['invoice']
                invoices_data.append({
                    'id': invoice.id,
                    'serie': invoice.serie,
                    'consecutive': invoice.consecutive,
                    'date': invoice.date.strftime("%Y-%m-%d"),
                    'due_date': invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else '',
                    'total_amount': float(invoice_data['total_amount']),
                    'paid_amount': float(invoice_data['paid_amount']),
                    'balance': float(invoice_data['balance']),
                })

            return JsonResponse({'invoices': invoices_data})

        return JsonResponse({'error': 'Acción no válida'})
