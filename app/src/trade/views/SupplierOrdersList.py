from django.views.generic import ListView
from trade.models import Order
from trade.models.Invoice import Invoice
from django.db.models import Sum
from datetime import datetime
from django.db.models import Q


# trade/supplier-orders/
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
        context['por_confirmar'] = self.get_por_confirmar()
        context['compras_facturadas'] = self.get_compras_facturadas()
        context['tallos_confirmados'] = self.get_tallos_confirmados()
        context['tallos_facturados'] = self.get_tallos_facturados()
        context['compras_mes'] = self.get_compras_mes()
        context['facturado_mes'] = self.get_facturado_mes()
        context['total_alerts'] = self.get_total_alerts()

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['message'] = 'Orden eliminada exitosamente'
        return context

    def get_order_alert(self, order):
        """
        Verifica si la orden de compra tiene inconsistencias con su orden de venta padre
        Retorna: dict con 'has_alert' (bool), 'message' (str) y 'type' (str)
        """
        # Si no tiene orden padre, no hay qué validar
        if not order.parent_order:
            return {
                'has_alert': False,
                'message': '',
                'type': None,
                'icon': None
            }
        
        parent_order = order.parent_order
        
        # Ignorar si la orden padre está en PROMESA
        if parent_order.status == 'PROMESA':
            return {
                'has_alert': False,
                'message': '',
                'type': None,
                'icon': None
            }
        
        # Verificar si los estados son diferentes
        if order.status != parent_order.status:
            return {
                'has_alert': True,
                'message': f'Estado de OC ({order.status}) diferente a OV {parent_order.serie}-{parent_order.consecutive:06d} ({parent_order.status})',
                'type': 'error',
                'icon': 'exclamation-circle'
            }
        
        # Si está facturada, verificar que existan las facturas
        if order.status == 'FACTURADO':
            invoice_compra = Invoice.objects.filter(
                order=order,
                type_document='FAC_COMPRA',
                is_active=True
            ).first()
            
            invoice_venta = Invoice.objects.filter(
                order=parent_order,
                type_document='FAC_VENTA',
                is_active=True
            ).first()
            
            if not invoice_compra:
                return {
                    'has_alert': True,
                    'message': 'Orden FACTURADA sin factura de compra',
                    'type': 'error',
                    'icon': 'exclamation-circle'
                }
            
            if not invoice_venta:
                return {
                    'has_alert': True,
                    'message': f'OV {parent_order.serie}-{parent_order.consecutive:06d} sin factura de venta',
                    'type': 'error',
                    'icon': 'exclamation-circle'
                }
        
        return {
            'has_alert': False,
            'message': '',
            'type': None,
            'icon': None
        }

    def get_total_alerts(self):
        """Cuenta el total de órdenes con alertas"""
        count = 0
        for order in self.get_queryset():
            if self.get_order_alert(order)['has_alert']:
                count += 1
        return count

    def get_por_confirmar(self):
        """Valor en dolares de Ordenes de compra sin factura en estado modificado y confirmado"""
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status__in=['MODIFICADO', 'CONFIRMADO'],
            is_invoiced=False,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_compras_facturadas(self):
        """El total de ordenes de compra que han sido facturados"""
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            is_invoiced=True,
            is_active=True
        ).count()

    def get_tallos_confirmados(self):
        """Total de tallos de los pedidos que estan confirmados"""
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            status='CONFIRMADO',
            is_active=True
        ).aggregate(total=Sum('total_stem_flower'))['total'] or 0

    def get_tallos_facturados(self):
        """Total de tallos de los pedidos que tienen factura"""
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            is_invoiced=True,
            is_active=True
        ).aggregate(total=Sum('total_stem_flower'))['total'] or 0

    def get_compras_mes(self):
        """Valor total de ordenes de compra por mes"""
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_facturado_mes(self):
        """Valor total facturado por mes"""
        today = datetime.now()
        return Order.objects.filter(
            type_document='ORD_COMPRA',
            is_invoiced=True,
            date__year=today.year,
            date__month=today.month,
            is_active=True
        ).aggregate(total=Sum('total_price'))['total'] or 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(
            type_document='ORD_COMPRA',
        ).select_related('parent_order', 'partner').order_by('-date')
        
        # Agregar información de alerta a cada orden
        for order in queryset:
            order.alert_info = self.get_order_alert(order)
        
        return queryset

