from common.AppLoger import loggin_event
from datetime import datetime, timedelta
from partners.models import DAE
from trade.models import (
    OrderBoxItems,
    OrderItems,
    Invoice,
    InvoiceItems,
    InvoiceBoxItems,
)


# Genera una factura a partir de una orden
# La orden de venta genera Factura con el consecutivo de kosmo
# la orden de compra se genera un factura que recibe el
# numero del proveedor luego de ser creada
class InvoiceOrder:
    def generate_invoice(self, order):
        """args: orden: Order"""
        loggin_event(f"Generando factura para la orden {order.id}")
        if order.status != 'CONFIRMADO':
            loggin_event(
                f"Orden {order.id} no puede ser facturada status {order.status}",
                error=True
            )
            return False

        if order.type_document == "ORD_VENTA":
            return self.gnerate_invoice_customer(order)

        return self.generate_invoice_supplier(order)

    def gnerate_invoice_customer(self, order):
        loggin_event(f"Generando factura para la ORDEN VENTA {order.id}")
        days = order.partner.credit_term
        due_date = datetime.now() + timedelta(days=days)
        dae = DAE.get_last_by_partner(order.partner)

        invoice = Invoice.objects.create(
            order=order,
            partner=order.partner,
            type_document='FAC_VENTA',
            date=datetime.now(),
            due_date=due_date,
            status='PENDIENTE',
            dae_export=dae.dae,
            awb=dae.awb,
            hawb=dae.hawb,
            cargo_agency=dae.cargo_agency
        )
        # cargamos los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
                order_item=oi,
                box_model=oi.box_model,
                id_order_item=oi.id,
                quantity=oi.quantity,
                tot_stem_flower=oi.tot_stem_flower,
                line_price=oi.line_price,
                line_margin=oi.line_margin,
                line_total=oi.line_total
            )
            order_box_items = OrderBoxItems.objects.filter(order_item=oi)
            for obx in order_box_items:
                InvoiceBoxItems.objects.create(
                    invoice_item=inv_item,
                    product=obx.product,
                    length=obx.length,
                    qty_stem_flower=obx.qty_stem_flower,
                    stem_cost_price=obx.stem_cost_price,
                    stem_price=obx.stem_price,
                    stem_margin=obx.stem_margin,
                )

        # calculamos los totales de la factura
        Invoice.rebuild_totals(invoice)
        order.is_invoiced = True
        order.id_invoice = invoice.id
        order.save()
        return invoice

    def generate_invoice_supplier(self, order):
        loggin_event(f"Generando factura para la ORDEN COMPRA {order.id}")
        invoice = Invoice.objects.create(
            order=order,
            partner=order.partner,
            type_document='FAC_COMPRA',
            total_price=order.total_price,
            status='PENDIENTE',
        )
        order_items = OrderItems.get_by_order(order.id)
        for oi in order_items:
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
                id_order_item=oi.id,
                box_model=oi.box_model,
                quantity=oi.quantity,
                tot_stem_flower=oi.tot_stem_flower,
                line_price=oi.line_price,
                line_margin=oi.line_margin,
                line_total=oi.line_total
            )
            order_box_items = OrderBoxItems.objects.filter(order_item=oi)
            for obx in order_box_items:
                InvoiceBoxItems.objects.create(
                    invoice_item=inv_item,
                    product=obx.product,
                    length=obx.length,
                    qty_stem_flower=obx.qty_stem_flower
                )
        return invoice
