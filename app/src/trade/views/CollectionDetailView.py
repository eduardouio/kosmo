
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Payment, PaymentDetail


class CollectionDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "presentations/collect_presentation.html"
    context_object_name = "collection"

    def get_queryset(self):
        """Filtra solo los cobros (ingresos)"""
        return Payment.objects.filter(type_transaction='INGRESO')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.get_object()

        # Obtener detalles del cobro con facturas relacionadas
        collection_details = PaymentDetail.objects.filter(
            payment=collection
        ).select_related(
            'invoice', 'invoice__partner'
        ).order_by('invoice__num_invoice')

        context['collection_details'] = collection_details
        context['total_invoices_amount'] = sum(
            detail.amount for detail in collection_details
        )
        context['invoices_count'] = collection_details.count()

        # Información adicional para la vista
        context['page_title'] = (
            f'Detalle del Cobro {collection.payment_number or collection.id}'
        )

        return context