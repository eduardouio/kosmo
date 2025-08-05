from django.views.generic import ListView
from trade.models import Payment
from django.db.models import Sum, Q
from datetime import date, datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from decimal import Decimal
from trade.models import Invoice


# cobros/
class CollectionsListView(LoginRequiredMixin, ListView):
    model = Payment
    template_name = 'lists/collections_list.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        """Filtra solo los cobros (ingresos)"""
        return Payment.objects.filter(
            type_transaction='INGRESO',
            is_active=True
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calcular cobros vencidos (total de monto)
        vencidos = Payment.objects.filter(
            type_transaction='INGRESO',
            status='PENDIENTE',
            due_date__lt=date.today(),
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Facturas cobradas (facturas con estado PAGADO para ventas)
        # Usando type_document en lugar de type_invoice, asumiendo que es 'VENTA' o similar
        fc_cobradas = Invoice.objects.filter(
            status='PAGADO',
            type_document='VENTA',  # Ajustar según el valor correcto en tu modelo
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        # Facturas pendientes por cobrar
        fc_por_cobrar = Invoice.objects.filter(
            ~Q(status='PAGADO'),
            type_document='VENTA',  # Ajustar según el valor correcto en tu modelo
            is_active=True
        ).count()

        # Cobros del mes actual
        current_month = datetime.now().month
        current_year = datetime.now().year
        cobros_mes = Payment.objects.filter(
            type_transaction='INGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Añadir al contexto
        context['vencidos'] = vencidos
        context['fc_cobradas'] = fc_cobradas
        context['fc_por_cobrar'] = fc_por_cobrar
        context['cobros_mes'] = cobros_mes

        return context
