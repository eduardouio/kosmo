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
            invoice = self.gnerate_invoice_customer(order)
        else:
            invoice = self.generate_invoice_supplier(order)

        order.is_invoiced = True
        order.id_invoice = invoice.id
        order.save()
        loggin_event(f'Factura generada correctamente {invoice.id}')
        Invoice.rebuild_totals(invoice)
        return invoice

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
            dae_export=dae.dae if dae else None,
            awb=dae.awb if dae else None,
            hawb=dae.hawb if dae else None,
            cargo_agency=dae.cargo_agency if dae else None
        )
        # cargamos los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
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
                    profit_margin=obx.profit_margin,
                )

        return invoice

    def generate_invoice_supplier(self, order):
        loggin_event(f"Generando factura para la ORDEN COMPRA {order.id}")
        days = order.partner.credit_term
        due_date = datetime.now() + timedelta(days=days)

        invoice = Invoice.objects.create(
            order=order,
            partner=order.partner,
            type_document='FAC_COMPRA',
            date=datetime.now(),
            due_date=due_date,
            status='PENDIENTE',
        )
        # cargamos los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
                id_order_item=oi.id,
                box_model=oi.box_model,
                quantity=oi.quantity,
                tot_stem_flower=oi.tot_stem_flower,
                line_price=oi.line_price,
                line_margin=oi.line_margin,
                line_total=oi.line_price
            )
            order_box_items = OrderBoxItems.objects.filter(order_item=oi)
            for obx in order_box_items:
                InvoiceBoxItems.objects.create(
                    invoice_item=inv_item,
                    product=obx.product,
                    length=obx.length,
                    qty_stem_flower=obx.qty_stem_flower,
                    stem_cost_price=obx.stem_cost_price,
                    profit_margin=obx.profit_margin,
                )

        return invoice
