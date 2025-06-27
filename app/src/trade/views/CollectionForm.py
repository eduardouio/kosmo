from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from trade.models.Payment import Payment, METHOD_CHOICES
from common.SaleInvoices import InvoiceBalance
from partners.models import Partner

import json
from decimal import Decimal


class CollectionFormView(LoginRequiredMixin, View):
    template_name = 'forms/collect_form.html'

    def get(self, request, collection_id=None):
        context = {
            'method_choices': METHOD_CHOICES,
            'partners': Partner.objects.filter(
                is_active=True, type_partner='CLIENTE'
            )
        }

        if collection_id:
            collection = get_object_or_404(Payment, id=collection_id)
            context['collection'] = collection

            # Obtener las facturas asociadas a este cobro
            invoices_in_collection = collection.invoices.all()
            context['invoices_in_collection'] = invoices_in_collection

        return render(request, self.template_name, context)

    def post(self, request, collection_id=None):
        # Implementación mejorada similar a PaymentFormView.post
        data = request.POST

        try:
            if collection_id:
                collection = get_object_or_404(Payment, id=collection_id)
                collection.invoices.clear()
            else:
                collection = Payment()
                collection.created_by = request.user

            # Datos básicos del cobro
            collection.date = data.get('date')
            collection.amount = Decimal(data.get('amount', '0.0'))
            collection.method = data.get('method')
            collection.bank = data.get('bank')
            collection.nro_account = data.get('nro_account')
            collection.nro_operation = data.get('nro_operation')
            collection.observations = data.get('observations', '')
            collection.updated_by = request.user

            # Manejo de archivo adjunto
            if 'document' in request.FILES:
                collection.document = request.FILES['document']

            collection.save()

            # Aplicar cobros a las facturas
            invoice_payments = json.loads(data.get('invoice_payments', '{}'))

            if invoice_payments:
                InvoiceBalance.apply_payment_to_invoices(
                    collection.id, invoice_payments
                )

            # Respuesta para AJAX
            content_type = request.headers.get('Content-Type', '')
            accept_header = request.headers.get('Accept', '')
            if ('application/json' in content_type or
                    'application/json' in accept_header):
                return JsonResponse({
                    'success': True,
                    'message': 'Cobro registrado correctamente',
                    'collection_id': collection.id
                })

            messages.success(request, "Cobro registrado correctamente")
            return redirect(reverse(
                'collection_detail', kwargs={'collection_id': collection.id}
            ))

        except Exception as e:
            error_message = f"Error al registrar el cobro: {str(e)}"

            # Respuesta para AJAX
            content_type = request.headers.get('Content-Type', '')
            accept_header = request.headers.get('Accept', '')
            if ('application/json' in content_type or
                    'application/json' in accept_header):
                return JsonResponse({
                    'success': False,
                    'error': error_message
                }, status=400)

            messages.error(request, error_message)
            return redirect(request.path)
