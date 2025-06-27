from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

from trade.models.Payment import Payment, METHOD_CHOICES
from trade.models.Invoice import Invoice
from common.SaleSupplierInvoices import SupplierInvoiceBalance
from partners.models import Partner

import json
from decimal import Decimal


class CollectFormView(LoginRequiredMixin, View):
    template_name = 'forms/collect_form.html'

    def get(self, request, collection_id=None):
        context = {
            'method_choices': METHOD_CHOICES,
            'partners': Partner.objects.filter(is_active=True, type_partner='CLIENTE')
        }

        if collection_id:
            collection = get_object_or_404(Payment, id=collection_id)
            context['collection'] = collection

            # Obtener las facturas asociadas a este cobro
            invoices_in_collection = collection.invoices.all()
            context['invoices_in_collection'] = invoices_in_collection

        return render(request, self.template_name, context)

    def post(self, request, collection_id=None):
        data = request.POST

        try:
            # Crear o actualizar cobro
            if collection_id:
                collection = get_object_or_404(Payment, id=collection_id)
                collection.invoices.clear()  # Eliminar asociaciones anteriores
            else:
                collection = Payment()
                collection.created_by = request.user

            # Actualizar datos del cobro
            collection.date = data.get('date')
            collection.amount = Decimal(data.get('amount', '0.0'))
            collection.method = data.get('method')
            collection.bank = data.get('bank')
            collection.nro_account = data.get('nro_account')
            collection.nro_operation = data.get('nro_operation')
            collection.updated_by = request.user
            collection.save()

            # Procesar facturas asociadas al cobro
            invoice_payments = json.loads(data.get('invoice_payments', '{}'))

            if invoice_payments:
                SupplierInvoiceBalance.apply_collection_to_invoices(
                    collection.id, invoice_payments)

            messages.success(request, "Cobro guardado correctamente")
            return redirect(reverse('collection_detail', kwargs={'collection_id': collection.id}))

        except Exception as e:
            messages.error(request, f"Error al guardar el cobro: {str(e)}")
            return redirect(request.path)


class CollectionApiView(View):
    def get(self, request):
        action = request.GET.get('action')

        if action == 'get_partner_invoices':
            partner_id = request.GET.get('partner_id')
            pending_invoices = SupplierInvoiceBalance.get_pending_invoices(
                partner_id)

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

        elif action == 'get_client_summary':
            partner_id = request.GET.get('partner_id')
            summary = SupplierInvoiceBalance.get_client_collection_summary(
                partner_id)

            return JsonResponse({
                'total_invoiced': float(summary['total_invoiced']),
                'total_collected': float(summary['total_collected']),
                'total_pending': float(summary['total_pending']),
                'invoices_count': summary['invoices_count'],
                'paid_invoices_count': summary['paid_invoices_count'],
                'pending_invoices_count': summary['pending_invoices_count']
            })

        return JsonResponse({'error': 'Acción no válida'})
