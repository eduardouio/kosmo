from django.views.generic import TemplateView
from trade.models import Invoice, InvoiceItems, InvoiceBoxItems, Order
from datetime import datetime
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event


class TemplateInvoice(TemplateView):
    template_name = 'reports/Invoice.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice_id = kwargs.get('id_invoice')
        invoice = Invoice.objects.get(pk=invoice_id)
        invoice_items = InvoiceItems.get_invoice_items(invoice)
        invoice_items_det = []
        for item in invoice_items:
            invoice_items_det.append({
                'item': item,
                'box_items': InvoiceBoxItems.get_box_items(item)
            })
        context['invoice'] = invoice
        context['invoice_items'] = invoice_items_det
        id_user_created = invoice.id_user_created if invoice.id_user_created else 1
        context['user_owner'] = CustomUserModel.get_by_id(id_user_created)
        context['now'] = datetime.now()

        import ipdb; ipdb.set_trace()

        # Obtener el nombre de la finca (proveedor) para la factura
        try:
            # La factura está asociada a una orden
            order = invoice.order
            farm_name = None

            if order.type_document == 'ORD_VENTA':
                # Si es una orden de venta, buscar el proveedor de la primera orden de compra relacionada
                purchase_orders = Order.get_purchase_orders_by_sale_order(
                    order)
                if purchase_orders and purchase_orders.exists():
                    # Usar el nombre del proveedor de la primera orden de compra relacionada
                    farm_name = purchase_orders.first().partner.name

            if not farm_name:
                # Si no se encontró un proveedor específico, usar un valor por defecto
                farm_name = "KOSMO FLOWERS"

            context['farm_name'] = farm_name
        except Exception as e:
            loggin_event(
                f"Error al obtener el nombre de la finca para la factura {invoice_id}: {str(e)}", error=True)
            context['farm_name'] = "KOSMO FLOWERS"

        return context
