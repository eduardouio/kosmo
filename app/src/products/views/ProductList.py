from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Min, Max, Q
from datetime import datetime, timedelta
from products.models import Product
from trade.models import Invoice, InvoiceBoxItems, Order, OrderBoxItems


# catalogo/lista/
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'lists/product_list.html'
    context_object_name = 'products'
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Obtener fecha del mes actual
        current_month = datetime.now().replace(day=1)
        next_month = (current_month.replace(day=28) +
                      timedelta(days=4)).replace(day=1)

        # Anotar cada producto con sus estadísticas del mes
        queryset = queryset.annotate(
            # Tallos vendidos en el mes (desde InvoiceBoxItems)
            stems_sold_month=Sum(
                'invoiceboxitems__qty_stem_flower',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__date__gte=current_month,
                    invoiceboxitems__invoice_item__invoice__date__lt=next_month,
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                )
            ) or 0,

            # Cantidad de facturas del mes
            invoices_count_month=Count(
                'invoiceboxitems__invoice_item__invoice',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__date__gte=current_month,
                    invoiceboxitems__invoice_item__invoice__date__lt=next_month,
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                ),
                distinct=True
            ) or 0,

            # Valor total en ventas del mes
            total_sales_month=Sum(
                'invoiceboxitems__qty_stem_flower',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__date__gte=current_month,
                    invoiceboxitems__invoice_item__invoice__date__lt=next_month,
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                )
            ) * Sum(
                'invoiceboxitems__stem_cost_price',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__date__gte=current_month,
                    invoiceboxitems__invoice_item__invoice__date__lt=next_month,
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                )
            ) or 0,

            # Costo máximo (precio más alto registrado)
            max_cost=Max(
                'invoiceboxitems__stem_cost_price',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                )
            ) or 0,

            # Costo mínimo (precio más bajo registrado)
            min_cost=Min(
                'invoiceboxitems__stem_cost_price',
                filter=Q(
                    invoiceboxitems__invoice_item__invoice__type_document='FAC_VENTA',
                    invoiceboxitems__invoice_item__invoice__is_active=True,
                    invoiceboxitems__is_active=True
                )
            ) or 0
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)
        context['title_section'] = 'Productos'
        context['title_page'] = 'Listado de Productos'
        context['action'] = None

        # Agregar fecha del mes actual para mostrar en la interfaz
        context['current_month'] = datetime.now().strftime('%B %Y')

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['action'] = 'deleted'
            context['message'] = 'Producto Eliminado Exitosamente'

        return context
