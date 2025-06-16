from django.views.generic import ListView
from trade.models import Invoice
from django.db import models
from django.utils import timezone
from django.utils.formats import number_format


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
        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Factura eliminada exitosamente'
        return context

    def get_queryset(self):
        return super().get_queryset().filter(
            type_document='FAC_VENTA',
            is_active=True,
        ).select_related('order', 'order__parent_order', 'partner').order_by('-date')

    def get_values_stats(self):
        invoices = self.get_queryset()
        active_invoices = invoices.filter(status='PENDIENTE').count()
        total_dued = invoices.filter(status='PENDIENTE').aggregate(models.Sum('total_price'))['total_price__sum'] or 0
        total_dued_this_month = invoices.filter(
            status='PENDIENTE',
            due_date__month=self.request.GET.get('month', timezone.now().month)
        ).aggregate(models.Sum('total_price'))['total_price__sum'] or 0
        total_for_charge = invoices.filter(status='PAGADO').aggregate(models.Sum('total_price'))['total_price__sum'] or 0
        total_stems_this_month = invoices.filter(
            delivery_date__month=self.request.GET.get('month', timezone.now().month)
        ).aggregate(models.Sum('tot_stem_flower'))['tot_stem_flower__sum'] or 0

        return {
            'active_invoices': active_invoices,
            'total_dued': f"$ {number_format(total_dued, decimal_pos=2)}",
            'total_dued_this_month': f"$ {number_format(total_dued_this_month, decimal_pos=2)}",
            'total_for_charge': f"$ {number_format(total_for_charge, decimal_pos=2)}",
            'total_stems_this_month': total_stems_this_month,
        }
