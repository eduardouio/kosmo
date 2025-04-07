from trade.models.Order import Order
from trade.models.Invoice import Invoice


class StatsSystem:
    @staticmethod
    def get_sales_stats():
        sales_orders = Order.objects.filter(
            type_document='ORD_VENTA',
            status__in=['MODIFICADO', 'PENDIENTE'],
            is_active=True
        )
        total_stems = sum(order.total_stem_flower for order in sales_orders)
        total_dollars = sum(order.total_price for order in sales_orders)
        return {
            'sales_orders_count': sales_orders.count(),
            'total_stems': total_stems,
            'total_dollars': total_dollars
        }

    @staticmethod
    def get_purchase_stats():
        purchase_orders = Order.objects.filter(
            type_document='ORD_COMPRA',
            status__in=['MODIFICADO', 'PENDIENTE'],
            is_active=True
        )
        total_stems = sum(order.total_stem_flower for order in purchase_orders)
        total_dollars = sum(order.total_price for order in purchase_orders)
        return {
            'purchase_orders_count': purchase_orders.count(),
            'total_stems': total_stems,
            'total_dollars': total_dollars
        }

    @staticmethod
    def get_sales_invoices_stats():
        sales_invoices = Invoice.objects.filter(
            type_document='FAC_VENTA',
            status__in=['PENDIENTE', 'PAGADO'],
            is_active=True
        )
        total_stems = sum(
            invoice.tot_stem_flower for invoice in sales_invoices)
        total_dollars = sum(invoice.total_price for invoice in sales_invoices)
        return {
            'sales_invoices_count': sales_invoices.count(),
            'total_stems': total_stems,
            'total_dollars': total_dollars
        }

    @staticmethod
    def get_purchase_invoices_stats():
        purchase_invoices = Invoice.objects.filter(
            type_document='FAC_COMPRA',
            status__in=['PENDIENTE', 'PAGADO'],
            is_active=True
        )
        total_stems = sum(
            invoice.tot_stem_flower for invoice in purchase_invoices)
        total_dollars = sum(
            invoice.total_price for invoice in purchase_invoices)
        return {
            'purchase_invoices_count': purchase_invoices.count(),
            'total_stems': total_stems,
            'total_dollars': total_dollars
        }

    @staticmethod
    def get_system_stats():
        return {
            'sales_stats': StatsSystem.get_sales_stats(),
            'purchase_stats': StatsSystem.get_purchase_stats(),
            'sales_invoices_stats': StatsSystem.get_sales_invoices_stats(),
            'purchase_invoices_stats': StatsSystem.get_purchase_invoices_stats()
        }
