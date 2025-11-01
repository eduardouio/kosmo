from django.views.generic import ListView
from trade.models import Invoice
from django.db import models
from django.utils import timezone
from django.utils.formats import number_format


# trade/customer-invoices/
class CustomerInvoiceList(ListView):
    model = Invoice
    template_name = 'lists/customer_invoices_list.html'
    context_object_name = 'invoices'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Facturas'
        context['title_page'] = 'Facturas de Clientes'
        context['action'] = None
        context['stats'] = self.get_values_stats()
        
        invoices_with_suppliers = []
        for invoice in context['invoices']:

            total_price = invoice.total_price or 0
            total_margin = invoice.total_margin or 0
            invoice.total_with_margin = total_price + total_margin
            

            if hasattr(invoice, 'order') and invoice.order:
                purchase_orders = invoice.order.order_set.filter(
                    type_document='ORD_COMPRA',
                    is_active=True
                )
                suppliers_info = []
                
                for purchase_order in purchase_orders:
                    has_partner = (hasattr(purchase_order, 'partner') and
                                   purchase_order.partner)
                    if has_partner:
                        partner_name = purchase_order.partner.name
                        supplier_name = partner_name or 'Sin nombre'
            
                        try:
                            from trade.models import Invoice as InvoiceModel
                            supplier_invoice = InvoiceModel.objects.get(
                                order=purchase_order,
                                type_document='FAC_COMPRA'
                            )
                            invoice_num = supplier_invoice.num_invoice
                            supplier_invoice_num = invoice_num or 'Sin número'
                        except InvoiceModel.DoesNotExist:
                            supplier_invoice_num = 'Sin Factura'
                        except Exception:
                            supplier_invoice_num = 'Error'
                        
                        suppliers_info.append({
                            'name': supplier_name,
                            'invoice_num': supplier_invoice_num
                        })
                
                invoice.suppliers_info = suppliers_info
            else:
                invoice.suppliers_info = []
            invoices_with_suppliers.append(invoice)
        
        context['invoices'] = invoices_with_suppliers
        
        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Factura eliminada exitosamente'
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            type_document='FAC_VENTA',
            is_active=True,
        ).select_related(
            'order', 'order__parent_order', 'partner'
        ).prefetch_related(
            'order__order_set'  # Órdenes de compra relacionadas
        ).order_by('-date')

    def get_values_stats(self):
        invoices = self.get_queryset()
        now = timezone.now()
        
        active_invoices = invoices.filter(status='PENDIENTE').count()
        
        total_for_charge = invoices.filter(status='PENDIENTE').aggregate(
            models.Sum('total_price'))['total_price__sum'] or 0
        
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
            'total_for_charge':
                f"$ {number_format(total_for_charge, decimal_pos=2)}",
            'total_stems_this_month': total_stems_this_month,
        }
