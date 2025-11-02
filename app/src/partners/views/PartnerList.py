from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from partners.models import Partner


# socios/clientes/ y socios/proveedores/
class PartnerListView(LoginRequiredMixin, ListView):
    model = Partner
    template_name = 'lists/partner_list.html'
    context_object_name = 'object_list'
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        source_page = self.kwargs.get('source_page', 'clientes')

        # Filtrar por tipo de partner
        if source_page == 'clientes':
            queryset = queryset.filter(
                type_partner='CLIENTE',
                is_active=True
            )

            # Estadísticas para clientes (facturas de venta)
            queryset = queryset.annotate(
                # Total en dólares de facturas de venta
                total_invoice_amount=Coalesce(
                    Sum(
                        'invoice__total_price',
                        filter=Q(
                            invoice__type_document='FAC_VENTA',
                            invoice__is_active=True
                        )
                    ),
                    Value(0, output_field=DecimalField(
                        max_digits=15, decimal_places=2))
                ),

                # Total de tallos vendidos
                total_stems_sold=Coalesce(
                    Sum(
                        'invoice__tot_stem_flower',
                        filter=Q(
                            invoice__type_document='FAC_VENTA',
                            invoice__is_active=True
                        )
                    ),
                    Value(0)
                ),

                # Total de pedidos sin facturar
                pending_orders=Coalesce(
                    Count(
                        'order',
                        filter=Q(
                            order__type_document='ORD_VENTA',
                            order__is_active=True,
                            order__is_invoiced=False
                        )
                    ),
                    Value(0)
                )
            )

        elif source_page == 'proveedores':
            queryset = queryset.filter(
                type_partner='PROVEEDOR',
                is_active=True
                )

            # Estadísticas para proveedores (facturas de compra)
            queryset = queryset.annotate(
                # Total en dólares de facturas de compra
                total_invoice_amount=Coalesce(
                    Sum(
                        'invoice__total_price',
                        filter=Q(
                            invoice__type_document='FAC_COMPRA',
                            invoice__is_active=True
                        )
                    ),
                    Value(0, output_field=DecimalField(
                        max_digits=15, decimal_places=2))
                ),

                # Total de tallos comprados
                total_stems_sold=Coalesce(
                    Sum(
                        'invoice__tot_stem_flower',
                        filter=Q(
                            invoice__type_document='FAC_COMPRA',
                            invoice__is_active=True
                        )
                    ),
                    Value(0)
                ),

                # Total de pedidos sin facturar
                pending_orders=Coalesce(
                    Count(
                        'order',
                        filter=Q(
                            order__type_document='ORD_COMPRA',
                            order__is_active=True,
                            order__is_invoiced=False
                        )
                    ),
                    Value(0)
                )
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source_page = self.kwargs.get('source_page', 'clientes')
        context['source_page'] = source_page

        if source_page == 'clientes':
            context['title_section'] = 'Clientes'
            context['title_page'] = 'Listado de Clientes'
        else:
            context['title_section'] = 'Proveedores'
            context['title_page'] = 'Listado de Proveedores'

        context['action'] = None

        if self.request.GET.get('action') == 'deleted':
            context['action_type'] = 'success'
            context['action'] = 'deleted'
            context['message'] = 'Partner Eliminado Exitosamente'

        return context
