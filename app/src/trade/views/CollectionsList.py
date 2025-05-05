from django.views.generic import ListView
from trade.models import Collection
from django.db.models import Sum, Count
from datetime import datetime
from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin


class CollectionsList(LoginRequiredMixin, ListView):
    """Vista basada en clase para listar todos los cobros con estadísticas"""
    model = Collection
    template_name = 'lists/collections_list.html'
    context_object_name = 'collections'
    
    def get_queryset(self):
        """Obtener todos los cobros activos ordenados por fecha descendente"""
        return Collection.objects.filter(is_active=True).order_by('-date')
    
    def get_context_data(self, **kwargs):
        """Añadir estadísticas adicionales al contexto"""
        context = super().get_context_data(**kwargs)
        
        # Obtener el queryset
        collections = self.get_queryset()
        
        # Obtener el mes y año actual
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Estadísticas de cobros
        stats = {
            # Número total de cobros activos
            'total_collections': collections.count(),
            
            # Cobros del mes actual
            'collections_this_month': collections.filter(
                date__month=current_month,
                date__year=current_year
            ).count(),
            
            # Total de monto cobrado en el mes actual
            'amount_this_month': collections.filter(
                date__month=current_month,
                date__year=current_year
            ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            
            # Total de monto cobrado de todos los tiempos
            'total_amount': collections.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
            
            # Cobros por método
            'collections_by_transfer': collections.filter(method='TRANSF').count(),
            'collections_by_check': collections.filter(method='CHEQUE').count(),
            'collections_by_cash': collections.filter(method='EFECTIVO').count(),
            'collections_by_credit_card': collections.filter(method='TC').count(),
            'collections_by_credit_note': collections.filter(method='NC').count(),
        }
        
        # Para cada cobro, obtener las facturas relacionadas
        for collection in context['collections']:
            collection.related_invoices = collection.invoices.all()
            # Calcular el número total de facturas relacionadas
            collection.invoice_count = collection.related_invoices.count()
        
        context['stats'] = stats
        context['current_month'] = datetime.now().strftime('%B %Y')
        
        return context
