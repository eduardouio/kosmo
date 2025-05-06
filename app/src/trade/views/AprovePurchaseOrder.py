from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Order
from common.AppLoger import loggin_event


class AprovePurchaseOrderView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('pk')
        loggin_event(f'AproveOrderView confirmando orden de compra {order_id}')

        order = get_object_or_404(Order, id=order_id)
        order.status = 'CONFIRMADO'
        order.save()

        if order.type_document == 'ORD_COMPRA':
            self.validate_supplier_order(cus_order=order.parent_order)
        else:
            self.aprove_sup_order(order)

        # Redirigir a la vista de detalle de la orden
        return redirect(reverse('order_detail_presentation', kwargs={'pk': order_id}))

    def validate_supplier_order(self, cus_order):
        loggin_event(f'AproveOrderView Validando ordenes hermanas {cus_order}')
        all_confirmed = True
        all_sup_orders = Order.get_by_parent_order(cus_order)
        for sup_order in all_sup_orders:
            if sup_order.status in ['PENDIENTE', 'MODIFICADO']:
                all_confirmed = False
                break

        if all_confirmed:
            loggin_event(
                f'AproveOrderView confirmando orden de compra {cus_order}'
            )
            cus_order.status = 'CONFIRMADO'
            cus_order.save()

    def aprove_sup_order(self, order):
        loggin_event(f'AproveOrderView Aprobando orden de compra {order}')
        order.status = 'CONFIRMADO'
        order.save()
        sup_order = Order.get_by_parent_order(order)
        for order in sup_order:
            order.status = 'CONFIRMADO'
            order.save()

        return order
