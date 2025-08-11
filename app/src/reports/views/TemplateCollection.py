from django.views.generic import TemplateView
from trade.models import Payment, PaymentDetail
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event
from datetime import datetime


class TemplateCollection(TemplateView):
    template_name = 'reports/collection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection_id = kwargs.get('id_collection')
        collection = Payment.objects.get(pk=collection_id)
        collection_details = PaymentDetail.objects.filter(
            payment=collection
        ).select_related('invoice', 'invoice__partner').order_by('invoice__num_invoice')
        
        # Obtener el usuario que creó el cobro
        user_created = None
        if collection.id_user_created:
            try:
                user_created = CustomUserModel.get_by_id(collection.id_user_created)
            except Exception as e:
                loggin_event(f"Error al obtener usuario creador del cobro {collection_id}: {str(e)}", error=True)
        
        context.update({
            'collection': collection,
            'collection_details': collection_details,
            'user_created': user_created,
            'now': datetime.now(),
            'total_invoices': collection_details.count(),
            'total_amount': collection.amount
        })
        
        return context