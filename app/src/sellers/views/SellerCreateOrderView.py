from django.views.generic import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from trade.models import Order, OrderItems
from partners.models import Partner
from products.models import StockDay, StockDetail, BoxItems
from common.AppLoger import loggin_event


class SellerCreateOrderView(LoginRequiredMixin, CreateView):
    """Vista para crear nuevas órdenes de venta"""
    model = Order
    template_name = 'seller/create_order_seller.html'
    success_url = reverse_lazy('sellers:orders')

    fields = [
        'partner', 'num_order', 'delivery_date',
        'discount', 'total_price', 'total_margin'
    ]

    def form_valid(self, form):
        """Configurar campos automáticos al crear orden"""
        try:
            # Configurar campos por defecto
            form.instance.type_document = 'ORD_VENTA'
            form.instance.status = 'PENDIENTE'

            # Obtener stock day actual
            current_stock = StockDay.objects.filter(
                is_active=True
            ).order_by('-date').first()
            if current_stock:
                form.instance.stock_day = current_stock

            response = super().form_valid(form)
            messages.success(
                self.request,
                f'Orden {form.instance.consecutive} creada exitosamente'
            )
            return response

        except Exception as e:
            loggin_event(f'Error creando orden: {e}')
            messages.error(
                self.request,
                'Error al crear la orden. Intente nuevamente.'
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = 'Crear Orden de Venta'
        
        # Obtener clientes activos
        ctx['customers'] = Partner.objects.filter(
            type_partner='C',
            is_active=True
        ).order_by('name')
        
        # Stock day actual
        ctx['current_stock_day'] = StockDay.objects.filter(
            is_active=True
        ).order_by('-date').first()
        
        # Manejar parámetros de stock preseleccionado
        stock_detail_id = self.request.GET.get('stock_detail')
        box_item_id = self.request.GET.get('box_item')
        
        if stock_detail_id:
            try:
                stock_detail = StockDetail.objects.get(
                    id=stock_detail_id,
                    is_active=True
                )
                ctx['preselected_stock'] = stock_detail
                ctx['preselected_partner'] = stock_detail.partner
            except StockDetail.DoesNotExist:
                pass
        
        elif box_item_id:
            try:
                box_item = BoxItems.objects.select_related(
                    'stock_detail__partner'
                ).get(id=box_item_id)
                ctx['preselected_box_item'] = box_item
                ctx['preselected_partner'] = box_item.stock_detail.partner
            except BoxItems.DoesNotExist:
                pass
        
        return ctx


class SellerEditOrderView(LoginRequiredMixin, UpdateView):
    """Vista para editar órdenes de venta (solo si están pendientes)"""
    model = Order
    template_name = 'seller/edit_order_seller.html'
    success_url = reverse_lazy('sellers:orders')

    fields = [
        'partner', 'num_order', 'delivery_date',
        'discount', 'status'
    ]

    def get_queryset(self):
        """Solo permitir editar órdenes de venta pendientes o modificadas"""
        return Order.objects.filter(
            type_document='ORD_VENTA',
            status__in=['PENDIENTE', 'MODIFICADO'],
            is_active=True
        )

    def form_valid(self, form):
        """Marcar como modificado si se edita"""
        try:
            if form.instance.status == 'PENDIENTE':
                form.instance.status = 'MODIFICADO'

            response = super().form_valid(form)
            messages.success(
                self.request,
                f'Orden {form.instance.consecutive} actualizada'
            )
            return response

        except Exception as e:
            loggin_event(f'Error editando orden: {e}')
            messages.error(
                self.request,
                'Error al actualizar la orden.'
            )
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = f'Editar Orden {self.object.consecutive}'

        # Obtener clientes activos
        ctx['customers'] = Partner.objects.filter(
            type_partner='C',
            is_active=True
        ).order_by('name')

        # Items de la orden
        ctx['order_items'] = OrderItems.objects.filter(
            order=self.object,
            is_active=True
        ).select_related('order')

        return ctx
