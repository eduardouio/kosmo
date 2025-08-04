from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Order, Invoice
from products.models import StockDay, StockDetail
from common.AppLoger import loggin_event
from common.StatsSystem import StatsSystem


class HomeTV(LoginRequiredMixin, TemplateView):
    template_name = 'pages/home.html'

    def get(self, request, *args, **kwargs):
        loggin_event(f'Acceso a la pagina de inicio {request.user}')
        page_data = {
            'title_page': 'Inicio',
            'module_name': 'Accounts',
            'user': request.user,
            'stats': self.get_stats(),
        }
        context = self.get_context_data(**kwargs)
        return self.render_to_response({**context, **page_data})

    def get_stats(self):
        last_stock = StockDay.objects.filter(
            is_active=True
        ).order_by('-date').first()

        total_orders = Order.objects.filter(
            type_document='ORD_VENTA',
            is_active=True,
            status__in=['PENDIENTE', 'MODIFICADO']
        )

        total_purchase_orders = Order.objects.filter(
            type_document='ORD_COMPRA',
            is_active=True,
            status__in=['PENDIENTE', 'MODIFICADO']
        )

        total_invoices = Invoice.objects.filter(
            type_document='FAC_VENTA',
            is_active=True,
            status__in=['PENDIENTE', 'MODIFICADO']
        )

        total_purchase_invoices = Invoice.objects.filter(
            type_document='FAC_COMPRA',
            is_active=True,
            status__in=['PENDIENTE', 'MODIFICADO']
        )

        total_stems = StockDetail.objects.filter(
            is_active=True,
            stock_day=last_stock
        )

        return {
            'total_stock': StockDay.objects.filter().count(),
            'last_stock': last_stock if last_stock else {'id': 0},
            'total_stems': sum(i.tot_stem_flower for i in total_stems),
            'total_orders': len(total_orders),
            'total_orders_stems': sum(i.total_stem_flower for i in total_orders),
            'total_purchase_orders': len(total_purchase_orders),
            'total_purchase_orders_stems': sum(i.total_stem_flower for i in total_purchase_orders),
            'total_invoices': len(total_invoices),
            'total_invoices_stems': sum(i.tot_stem_flower for i in total_invoices),
            'total_purchase_invoices': len(total_purchase_invoices),
            'total_purchase_invoices_stems': sum(i.tot_stem_flower for i in total_purchase_invoices),
            'general_stats': StatsSystem.get_system_stats(),
        }
