from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from trade.models import Order
from common.AppLoger import loggin_event


class SellerInvoiceView(LoginRequiredMixin, ListView):
    """Vista para mostrar facturas/órdenes facturadas"""
    model = Order
    template_name = 'seller/invoice_seller.html'
    context_object_name = 'invoices'
    paginate_by = 15

    def get_queryset(self):
        """Filtrar órdenes facturadas"""
        try:
            queryset = Order.objects.filter(
                type_document='ORD_VENTA',
                status='FACTURADO',
                is_active=True
            ).select_related('partner', 'stock_day').order_by('-date')

            # Filtro por búsqueda
            search = self.request.GET.get('search')
            if search:
                queryset = queryset.filter(
                    Q(consecutive__icontains=search) |
                    Q(partner__name__icontains=search) |
                    Q(num_invoice__icontains=search) |
                    Q(num_order__icontains=search)
                )

            return queryset

        except Exception as e:
            loggin_event(f'Error obteniendo facturas: {e}')
            return Order.objects.none()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title_page'] = 'Facturas'

        # Filtros activos
        ctx['current_search'] = self.request.GET.get('search', '')

        # Estadísticas
        all_invoices = self.get_queryset()
        ctx['total_invoices'] = all_invoices.count()
        ctx['total_amount'] = sum(
            invoice.total_price for invoice in all_invoices
        )
        ctx['total_stems'] = sum(
            invoice.total_stem_flower or 0 for invoice in all_invoices
        )
        ctx['total_margin'] = sum(
            invoice.total_margin for invoice in all_invoices
        )

        return ctx
