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
        """Filtra solo los cobros (ingresos) con relaciones optimizadas"""
        return Payment.objects.filter(
            type_transaction='INGRESO',
            is_active=True
        ).select_related().prefetch_related(
            'invoices__invoice__partner',
            'invoices__invoice'
        ).order_by('-date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Obtener mes y año actual
        current_month = datetime.now().month
        current_year = datetime.now().year

        # 1. Número de Cobros Realizados en el mes
        cobros_mes_count = Payment.objects.filter(
            type_transaction='INGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).count()

        # 2. Valor de cobros del mes
        cobros_mes = Payment.objects.filter(
            type_transaction='INGRESO',
            date__month=current_month,
            date__year=current_year,
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 3. Total Pendiente (cobros con estado PENDIENTE)
        total_pendiente = Payment.objects.filter(
            type_transaction='INGRESO',
            status='PENDIENTE',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # 4. Total Confirmado (cobros con estado CONFIRMADO)
        total_confirmado = Payment.objects.filter(
            type_transaction='INGRESO',
            status='CONFIRMADO',
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Calcular cobros vencidos (total de monto) - mantenido por compatibilidad
        vencidos = Payment.objects.filter(
            type_transaction='INGRESO',
            status='PENDIENTE',
            due_date__lt=date.today(),
            is_active=True
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Facturas cobradas (facturas con estado PAGADO para ventas)
        fc_cobradas = Invoice.objects.filter(
            status='PAGADO',
            type_document='FAC_VENTA',  # Corregido según las opciones del modelo
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')

        # Facturas pendientes por cobrar
        fc_por_cobrar = Invoice.objects.filter(
            ~Q(status='PAGADO'),
            type_document='FAC_VENTA',  # Corregido según las opciones del modelo
            is_active=True
        ).count()

        # Añadir al contexto las nuevas variables
        context['cobros_mes_count'] = cobros_mes_count
        context['cobros_mes'] = cobros_mes
        context['total_pendiente'] = total_pendiente  
        context['total_confirmado'] = total_confirmado
        context['vencidos'] = vencidos
        context['fc_cobradas'] = fc_cobradas
        context['fc_por_cobrar'] = fc_por_cobrar

        return context
