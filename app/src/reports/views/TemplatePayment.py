from django.views.generic import TemplateView
from trade.models import Payment, PaymentDetail
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event
from datetime import datetime


class TemplatePayment(TemplateView):
    template_name = 'reports/payment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        payment_id = kwargs.get('id_payment')
        payment = Payment.objects.get(pk=payment_id)
        payment_details = PaymentDetail.objects.filter(
            payment=payment
        ).select_related('invoice', 'invoice__partner').order_by('invoice__num_invoice')
        
        # Obtener el usuario que creó el pago
        user_created = None
        if payment.id_user_created:
            try:
                user_created = CustomUserModel.get_by_id(payment.id_user_created)
            except Exception as e:
                loggin_event(f"Error al obtener usuario creador del pago {payment_id}: {str(e)}", error=True)
        
        context.update({
            'payment': payment,
            'payment_details': payment_details,
            'user_created': user_created,
            'now': datetime.now(),
            'total_invoices': payment_details.count(),
            'total_amount': payment.amount
        })
        
        return context
