from common.AppLoger import loggin_event
from datetime import datetime, timedelta
from partners.models import DAE
from trade.models import (
    Order,
    OrderBoxItems,
    OrderItems,
    Invoice,
    InvoiceItems,
    InvoiceBoxItems,
)


class CreateInvoiceByOrder:
    def generate_invoice(self, order):
        """args: orden: Order"""
        loggin_event(f"Generando factura para la orden {order.id}")
        if order.status != 'CONFIRMADO':
            loggin_event(
                f"Orden {order.id} no puede ser facturada status {order.status}",
                error=True
            )
            return False

        if order.is_invoiced:
            loggin_event(
                f"Orden {order.id} ya fue facturada",
                error=True
            )
            return Invoice.get_by_id(order.id_invoice)

        if order.type_document == "ORD_VENTA":
            invoice = self.gnerate_invoice_customer(order)
            supp_orders = Order.get_by_parent_order(order)
            for supp_order in supp_orders:
                sup_invoice = self.generate_invoice_supplier(supp_order)
                if not sup_invoice:
                    loggin_event(
                        f"Error generando factura para la orden {supp_order.id}",
                        error=True
                    )
                    break
                supp_order.status = 'FACTURADO'
                supp_order.is_invoiced = True
                supp_order.id_invoice = sup_invoice.id
                supp_order.num_invoice = sup_invoice.num_invoice
                supp_order.save()
                loggin_event(
                    f"Factura relacionada generada correctamente {sup_invoice.id}"
                )
                Invoice.rebuild_totals(sup_invoice)
        else:
            invoice = self.generate_invoice_supplier(order)

        order.status = 'FACTURADO'
        order.is_invoiced = True
        order.id_invoice = invoice.id
        order.num_invoice = invoice.num_invoice
        order.save()
        loggin_event(f'Factura generada correctamente {invoice.id}')
        Invoice.rebuild_totals(invoice)
        return invoice

    def gnerate_invoice_customer(self, order):
        loggin_event(f"Generando factura para la ORDEN VENTA {order.id}")
        totals = {
            'qb_total': 0,
            'hb_total': 0,
            'tot_stem_flower': 0,
            'total_price': 0,
            'total_margin': 0,
            'fb_total': 0,
            'total_pieces': 0,
        }
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
            cargo_agency=dae.cargo_agency if dae else None,
            serie='001',
            consecutive=Invoice.get_next_sale_consecutive()
            
        )
        # cargamos los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            totals['qb_total'] += oi.qb_total
            totals['hb_total'] += oi.hb_total
            totals['total_pieces'] += oi.quantity
            totals['tot_stem_flower'] += oi.tot_stem_flower
            totals['total_price'] += oi.line_price
            totals['total_margin'] += oi.line_margin

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

        invoice.qb_total = totals['qb_total']
        invoice.hb_total = totals['hb_total']
        invoice.fb_total = ((totals['qb_total']/2)+totals['hb_total'])/2
        invoice.tot_stem_flower = totals['tot_stem_flower']
        invoice.total_price = totals['total_price']
        invoice.total_margin = totals['total_margin']
        invoice.total_pieces = totals['total_pieces']

        return invoice

    def generate_invoice_supplier(self, order):
        if order.is_invoiced:
            loggin_event(
                f"Orden {order.id} ya fue facturada",
                error=True
            )
            return False

        loggin_event(f"Generando factura para la ORDEN COMPRA {order.id}")
        days = order.partner.credit_term
        due_date = datetime.now() + timedelta(days=days)

        # Crear número de factura con formato SinFact-{serie-consecutivo}
        num_invoice = f"SinFact-{order.serie or '200'}-{str(order.consecutive or 0).zfill(6)}"

        invoice = Invoice.objects.create(
            order=order,
            partner=order.partner,
            type_document='FAC_COMPRA',
            date=datetime.now(),
            due_date=due_date,
            status='PENDIENTE',
            num_invoice=num_invoice,
            serie='',  # Serie en blanco
            consecutive=None  # Consecutivo en blanco
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
