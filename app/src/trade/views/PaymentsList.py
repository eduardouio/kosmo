from django.views.generic import ListView
from trade.models import Payment
from django.db.models import Sum, Count
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin


class PaymentsList(LoginRequiredMixin, ListView):
    """Vista basada en clase para listar todos los pagos con estadísticas"""
    model = Payment
    template_name = 'lists/payments_list.html'
    context_object_name = 'payments'
    
    def get_queryset(self):
        """Obtener todos los pagos activos ordenados por fecha descendente"""
        return Payment.objects.filter(is_active=True).order_by('-date')
    
    def get_context_data(self, **kwargs):
        """Añadir estadísticas adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        
        # Obtener el queryset
        payments = self.get_queryset()
        
        # Obtener el mes y año actual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Estadísticas de pagos
        stats = {
            # Número total de pagos activos
            'total_payments': payments.count(),
            
            # Pagos del mes actual
            'payments_this_month': payments.filter(
                date__month=current_month,
                date__year=current_year
            ).count(),
            
            # Total de monto pagado en el mes actual
            'amount_this_month': payments.filter(
                date__month=current_month,
                date__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            
            # Total de monto pagado de todos los tiempos
            'total_amount': payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            
            # Pagos por método
            'payments_by_transfer': payments.filter(method='TRANSF').count(),
            'payments_by_check': payments.filter(method='CHEQUE').count(),
            'payments_by_cash': payments.filter(method='EFECTIVO').count(),
            'payments_by_credit_card': payments.filter(method='TC').count(),
            'payments_by_credit_note': payments.filter(method='NC').count(),
        }
        
        # Para cada pago, obtener las facturas relacionadas
        for payment in context['payments']:
            payment.related_invoices = payment.invoices.all()
            # Calcular el número total de facturas relacionadas
            payment.invoice_count = payment.related_invoices.count()
        
        context['stats'] = stats
        context['current_month'] = datetime.now().strftime('%B %Y')
        
        return context
