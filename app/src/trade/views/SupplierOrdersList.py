from django.views.generic import ListView
from trade.models import Order
from django.db.models import Sum
from datetime import datetime
from django.db.models import Q


class SupplierOrdersList(ListView):
    model = Order
    template_name = 'lists/supplier_orders_list.html'
    context_object_name = 'orders'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title_section'] = 'Listado de Órdenes a Proveedores'
        context['title_page'] = 'Ordenes a Proveedores'
        context['action'] = None

        # Agregar estadísticas
        context['pending_modified_count'] = self.get_pending_modified_count()
        context['current_month_invoiced'] = self.get_current_month_invoiced()
        context['current_month_stems'] = self.get_current_month_stems()
        context['current_month_total'] = self.get_current_month_total()
        context['pending_modified_total'] = self.get_pending_modified_total()

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Orden eliminada exitosamente'
        return context

    def get_pending_modified_count(self):
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status__in=['PENDIENTE', 'MODIFICADO'],
            is_active=True
        ).count()

    def get_current_month_invoiced(self):
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status='FACTURADO',
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).count()

    def get_current_month_stems(self):
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status='FACTURADO',
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_stem_flower'))['total'] or 0

    def get_current_month_total(self):
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status='FACTURADO',
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_pending_modified_total(self):
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status__in=['PENDIENTE', 'MODIFICADO'],
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_queryset(self):
        return super().get_queryset().filter(
            type_document='ORD_COMPRA',
        ).order_by('-date')

