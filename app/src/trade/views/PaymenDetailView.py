

from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Payment, PaymentDetail


class PaymenDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "presentations/payment_detail.html"
    context_object_name = "payment"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment = self.get_object()
        
        # Obtener detalles del pago con facturas relacionadas
        payment_details = PaymentDetail.objects.filter(
            payment=payment
        ).select_related(
            'invoice', 'invoice__partner'
        ).order_by('invoice__num_invoice')
        
        context['payment_details'] = payment_details
        context['total_invoices_amount'] = sum(
            detail.amount for detail in payment_details
        )
        context['invoices_count'] = payment_details.count()
        
        # Información adicional para la vista
        context['page_title'] = (
            f'Detalle del Pago {payment.payment_number or payment.id}'
        )
        
        return context