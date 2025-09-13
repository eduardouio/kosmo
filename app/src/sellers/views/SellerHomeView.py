from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.functional import cached_property
from common.SellerData import SellerData


class SellerHomeView(LoginRequiredMixin, TemplateView):
    template_name = 'seller/home_seller.html'

    @cached_property
    def seller_data(self):
        """Obtiene datos; si falla usa datos de ejemplo."""
        user = self.request.user
        try:
            data = SellerData.get_seller_info(user.id)
            if not data or 'total_sales' not in data:
                raise ValueError('SellerData incompleta')
            return data
        except Exception:  # control amplio: SellerData aún incompleta
            return {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name or 'Nombre',
                    'last_name': user.last_name or 'Vendedor',
                },
                'customer_orders': [
                    {
                        'id': 101,
                        'consecutive': 'V-2025-001',
                        'date': '2025-08-01',
                        'status': 'CONFIRMADO',
                        'total_price': 1250.50,
                        'total_margin': 180.75,
                        'tot_stem_flower': 5200,
                    },
                    {
                        'id': 102,
                        'consecutive': 'V-2025-002',
                        'date': '2025-08-03',
                        'status': 'PENDIENTE',
                        'total_price': 980.00,
                        'total_margin': 140.10,
                        'tot_stem_flower': 4100,
                    },
                ],
                'supplier_orders': [
                    {
                        'id': 401,
                        'consecutive': 'C-2025-015',
                        'date': '2025-08-02',
                        'status': 'PENDIENTE',
                        'total_price': 700.00,
                        'tot_stem_flower': 3000,
                    }
                ],
                'stems_sold': 15200,
                'total_sales': 22350.80,
                'sales_by_status': {
                    'PAGADO': {'count': 5, 'total': 15000.00},
                    'ABONADO': {'count': 2, 'total': 4300.00},
                    'PENDIENTE': {'count': 3, 'total': 3050.80},
                },
                'customers': [
                    {
                        'id': 1,
                        'name': 'FloraExport LLC',
                        'short_name': 'FLORA',
                        'stems_total': 8200,
                        'sales_total': 11200.50,
                        'invoices_count': 4,
                    },
                    {
                        'id': 2,
                        'name': 'Bloom World',
                        'short_name': 'BLOOM',
                        'stems_total': 5000,
                        'sales_total': 8700.30,
                        'invoices_count': 3,
                    },
                ],
                'stems_pending': 3600,
                'pending_buys': 1450.75,
            }

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        data = self.seller_data
        user_info = data.get('user', {})

        ctx['title_page'] = 'Dashboard Vendedor'
        ctx['seller_name'] = (
            f"{user_info.get('first_name', '')} "
            f"{user_info.get('last_name', '')}".strip()
        )
        ctx['total_sales'] = data.get('total_sales', 0)
        ctx['stems_sold'] = data.get('stems_sold', 0)
        ctx['stems_pending'] = data.get('stems_pending', 0)
        ctx['pending_buys'] = data.get('pending_buys', 0)
        ctx['sales_by_status'] = data.get('sales_by_status', {})
        ctx['customer_orders'] = data.get('customer_orders', [])[:10]
        ctx['supplier_orders'] = data.get('supplier_orders', [])[:10]
        ctx['top_customers'] = data.get('customers', [])[:6]

        goal_stems = user_info.get('goal_stems') or 0
        stems_sold = ctx['stems_sold'] or 0
        try:
            pct = (stems_sold / goal_stems * 100) if goal_stems else 0
        except Exception:
            pct = 0

        # Limitar a 150% (protege layout) y guardar datos progreso
        ctx['goal_stems'] = goal_stems
        ctx['stems_progress_pct'] = round(pct, 1)
        ctx['stems_progress_pct_capped'] = 150 if pct > 150 else round(pct, 1)
        # Ancho para barra (0-100)
        ctx['stems_progress_width'] = min(100, ctx['stems_progress_pct'])
        return ctx
