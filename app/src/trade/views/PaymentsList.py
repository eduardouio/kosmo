from django.views.generic import ListView
from trade.models import Payment, Invoice
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import date, datetime
from django.db.models import Sum, Q
from decimal import Decimal


class PaymentsList(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'lists/payments_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        """Filtra solo los pagos (egresos)"""
        return Payment.objects.filter(
            type_transaction='EGRESO',
            is_active=True
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calcular pagos vencidos (total de monto)
        vencidos = Payment.objects.filter(
            type_transaction='EGRESO',
            status='PENDIENTE',
            due_date__lt=date.today(),
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Facturas pagadas (facturas con estado PAGADO)
        fc_pagadas = Invoice.objects.filter(
            status='PAGADO',
            type_document='FAC_VENTA',
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        # Facturas pendientes por pagar
        fc_por_pagar = Invoice.objects.filter(
            ~Q(status='PAGADO'),
            type_document='FAC_VENTA',
            is_active=True
        ).count()

        # Pagos del mes actual
        current_month = datetime.now().month
        current_year = datetime.now().year
        pagos_mes = Payment.objects.filter(
            type_transaction='EGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Añadir al contexto
        context['vencidos'] = vencidos
        context['fc_pagadas'] = fc_pagadas
        context['fc_por_pagar'] = fc_por_pagar
        context['pagos_mes'] = pagos_mes

        return context
