from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from trade.models import Order
from common.AppLoger import loggin_event


class AprovePurchaseOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('pk')
        loggin_event(f'AproveOrderView confirmando orden {order_id}')

        order = get_object_or_404(Order, id=order_id)

        # Validar que la orden esté en estado que permita confirmación
        if order.status not in ['PENDIENTE', 'MODIFICADO']:
            messages.error(
                request, f'La orden no puede ser confirmada. Estado actual: {order.status}')
            return redirect(reverse('order_detail_presentation', kwargs={'pk': order_id}))

        old_status = order.status
        order.status = 'CONFIRMADO'
        order.save()

        loggin_event(
            f'Orden {order_id} confirmada: {old_status} -> CONFIRMADO')

        # Lógica específica según el tipo de documento
        if order.type_document == 'ORD_COMPRA':
            self.validate_supplier_order(cus_order=order.parent_order)
        elif order.type_document == 'ORD_VENTA':
            self.aprove_sale_order(order)

        order_type = 'venta' if order.type_document == 'ORD_VENTA' else 'compra'
        messages.success(
            request, f'Orden de {order_type} {order.num_order or order_id} confirmada exitosamente.')

        # Redirigir a la vista de detalle de la orden
        return redirect(reverse('order_detail_presentation', kwargs={'pk': order_id}))

    def post(self, request, *args, **kwargs):
        # Manejar POST requests igual que GET
        return self.get(request, *args, **kwargs)

    def validate_supplier_order(self, cus_order):
        """Validar si todas las órdenes de compra de una orden de venta están confirmadas"""
        if not cus_order:
            return

        loggin_event(f'AproveOrderView Validando ordenes hermanas {cus_order}')
        all_confirmed = True
        all_sup_orders = Order.get_by_parent_order(cus_order)

        if all_sup_orders:
            for sup_order in all_sup_orders:
                if sup_order.status in ['PENDIENTE', 'MODIFICADO']:
                    all_confirmed = False
                    break

            if all_confirmed:
                loggin_event(
                    f'AproveOrderView confirmando orden de venta padre {cus_order}'
                )
                cus_order.status = 'CONFIRMADO'
                cus_order.save()

    def aprove_sale_order(self, order):
        """Aprobar orden de venta y sus órdenes de compra relacionadas"""
        loggin_event(f'AproveOrderView Aprobando orden de venta {order}')

        # Confirmar todas las órdenes de compra relacionadas
        sup_orders = Order.get_by_parent_order(order)
        if sup_orders:
            for sup_order in sup_orders:
                sup_order.status = 'CONFIRMADO'
                sup_order.save()
                loggin_event(
                    f'Orden de compra {sup_order.id} confirmada automáticamente')

        return order
