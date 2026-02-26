from django.views.generic import ListView
from trade.models import Invoice
from django.db import models
from django.utils import timezone
from django.utils.formats import number_format


# trade/supplier-invoices/
class SupplierInvoiceList(ListView):
    model = Invoice
    template_name = 'lists/supplier_invoices_list.html'
    context_object_name = 'invoices'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Facturas'
        context['title_page'] = 'Facturas de Provedores'
        context['action'] = None
        context['stats'] = self.get_values_stats()

        invoices_with_customers = []
        for invoice in context['invoices']:
            if (hasattr(invoice, 'order') and invoice.order and
                    hasattr(invoice.order, 'parent_order') and
                    invoice.order.parent_order):
                sale_order = invoice.order.parent_order
                if hasattr(sale_order, 'partner') and sale_order.partner:
                    partner_name = sale_order.partner.name
                    invoice.customer_name = partner_name or 'Sin nombre'
                    
                    from trade.models import Invoice as InvoiceModel
                    customer_invoices = InvoiceModel.objects.filter(
                        order=sale_order,
                        type_document='FAC_VENTA',
                        is_active=True
                    ).order_by('-date')

                    count = customer_invoices.count()
                    if count > 1:
                        # Múltiples facturas: marcar error y listar todas
                        invoice.customer_invoice_num = 'Error'
                        invoice.customer_invoices_list = list(
                            customer_invoices.values_list('id', 'num_invoice')
                        )
                    elif count == 1:
                        customer_invoice = customer_invoices.first()
                        invoice_num = customer_invoice.num_invoice
                        invoice.customer_invoice_num = (invoice_num or
                                                        'Sin número')
                        invoice.customer_invoices_list = None
                    else:
                        invoice.customer_invoice_num = 'Sin Factura'
                        invoice.customer_invoices_list = None
                else:
                    invoice.customer_name = 'Sin Cliente'
                    invoice.customer_invoice_num = 'N/A'
            else:
                invoice.customer_name = 'Sin Cliente'
                invoice.customer_invoice_num = 'N/A'
            
            invoices_with_customers.append(invoice)
        
        context['invoices'] = invoices_with_customers

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Factura eliminada exitosamente'
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            type_document='FAC_COMPRA',
            is_active=True
        ).select_related(
            'order', 'order__parent_order', 'partner'
        ).order_by('-date')

    def get_values_stats(self):
        invoices = self.get_queryset()
        now = timezone.now()

        active_invoices = invoices.filter(status='PENDIENTE').count()

        total_dued_this_month = invoices.filter(
            status='PENDIENTE',
            due_date__month=now.month,
            due_date__year=now.year,
            due_date__gte=now.date()
        ).aggregate(models.Sum('total_price'))['total_price__sum'] or 0

        total_dued = invoices.filter(
            status='PENDIENTE',
            due_date__lt=now.date()
        ).aggregate(models.Sum('total_price'))['total_price__sum'] or 0

        total_stems_this_month = invoices.filter(
            date__month=now.month,
            date__year=now.year
        ).aggregate(models.Sum('tot_stem_flower'))['tot_stem_flower__sum'] or 0

        return {
            'active_invoices': active_invoices,
            'total_dued': f"$ {number_format(total_dued, decimal_pos=2)}",
            'total_dued_this_month':
                f"$ {number_format(total_dued_this_month, decimal_pos=2)}",
            'total_stems_this_month': total_stems_this_month,
        }
