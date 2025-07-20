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
        # Recalcular los totales para asegurar valores correctos
        Invoice.rebuild_totals(invoice)
        return invoice

    def gnerate_invoice_customer(self, order):
        loggin_event(f"Generando factura para la ORDEN VENTA {order.id}")

        days = order.partner.credit_term
        due_date = datetime.now() + timedelta(days=days)
        dae = DAE.get_last_by_partner(order.partner)

        # Obtener el consecutivo y generar el número de factura con formato
        consecutive = Invoice.get_next_sale_consecutive()
        num_invoice = f"100-{str(consecutive).zfill(6)}"

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
            serie='100',
            consecutive=consecutive,
            num_invoice=num_invoice
        )

        # Copiar los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
                box_model=oi.box_model,
                id_order_item=oi.id,
                quantity=oi.quantity,
                tot_stem_flower=oi.tot_stem_flower,
                total_bunches=oi.total_bunches,
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
                    # Asegurarse de usar el profit_margin del ítem
                    profit_margin=obx.profit_margin,
                    total_bunches=obx.total_bunches,
                    stems_bunch=obx.stems_bunch,
                )

        # Tomar los totales directamente de la orden
        invoice.qb_total = order.qb_total
        invoice.hb_total = order.hb_total
        invoice.eb_total = order.eb_total
        invoice.fb_total = order.fb_total
        invoice.tot_stem_flower = order.total_stem_flower
        invoice.total_price = order.total_price
        invoice.total_margin = order.total_margin
        # Calcular total_pieces de la orden
        order_items = OrderItems.get_by_order(order.id)
        total_pieces = sum(oi.quantity for oi in order_items)
        invoice.total_pieces = total_pieces
        invoice.total_bunches = order.total_bunches
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
        serie = order.serie or '200'
        consecutive = str(order.consecutive or 0).zfill(6)
        num_invoice = f"SinFact-{serie}-{consecutive}"

        invoice = Invoice.objects.create(
            order=order,
            partner=order.partner,
            type_document='FAC_COMPRA',
            date=datetime.now(),
            due_date=due_date,
            status='PENDIENTE',
            num_invoice=num_invoice,
            serie='',  # Serie en blanco
            consecutive=None,  # Consecutivo en blanco
            # Añadir los totales directamente de la orden
            total_price=order.total_price,
            total_margin=order.total_margin,
            qb_total=order.qb_total,
            hb_total=order.hb_total,
            fb_total=order.fb_total,
            eb_total=order.eb_total,
            tot_stem_flower=order.total_stem_flower,
            total_bunches=order.total_bunches
        )
        # cargamos los items de la orden a la factura
        for oi in OrderItems.get_by_order(order.id):
            inv_item = InvoiceItems.objects.create(
                invoice=invoice,
                id_order_item=oi.id,
                box_model=oi.box_model,
                quantity=oi.quantity,
                tot_stem_flower=oi.tot_stem_flower,
                total_bunches=oi.total_bunches,  # Agregar total_bunches
                line_price=oi.line_price,
                line_margin=oi.line_margin,
                # Usar line_total en lugar de line_price
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
                    total_bunches=obx.total_bunches,  # Agregar total_bunches
                    stems_bunch=obx.stems_bunch,  # Agregar stems_bunch
                )

        return invoice
