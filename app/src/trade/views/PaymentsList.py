from django.views.generic import ListView
from trade.models import Payment
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime
from django.db.models import Sum
from decimal import Decimal


# pagos/
class PaymentsList(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'lists/payments_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        """Filtra solo los pagos (egresos) con relaciones optimizadas"""
        return Payment.objects.filter(
            type_transaction='EGRESO'
        ).select_related().prefetch_related(
            'invoices__invoice__partner',
            'invoices__invoice'
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener mes y año actual
        current_month = datetime.now().month
        current_year = datetime.now().year

        # 1. Número de Pagos Realizados en el mes
        pagos_mes_count = Payment.objects.filter(
            type_transaction='EGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).count()

        # 2. Valor de pagos del mes (ya existía, lo mantenemos)
        pagos_mes = Payment.objects.filter(
            type_transaction='EGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 3. Total Pendiente (pagos con estado PENDIENTE)
        total_pendiente = Payment.objects.filter(
            type_transaction='EGRESO',
            status='PENDIENTE',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 4. Total Confirmado (pagos con estado CONFIRMADO)
        total_confirmado = Payment.objects.filter(
            type_transaction='EGRESO',
            status='CONFIRMADO',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Añadir al contexto las nuevas variables
        context['pagos_mes_count'] = pagos_mes_count
        context['pagos_mes'] = pagos_mes
        context['total_pendiente'] = total_pendiente
        context['total_confirmado'] = total_confirmado

        return context
