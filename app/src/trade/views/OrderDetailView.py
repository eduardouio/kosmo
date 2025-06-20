from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from trade.models import Order, OrderItems, OrderBoxItems, Invoice, InvoiceItems, InvoiceBoxItems
from partners.models import Partner


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'presentations/order_presentation.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        order = self.object

        context['title_section'] = f"Orden {order.num_order}"
        context['title_page'] = f"Orden {order.serie}-{str(order.consecutive).zfill(6)}"

        customer = order.partner
        supplier = None

        supplier_orders_qs = []
        if order.type_document == 'ORD_VENTA':
            supplier_orders_qs = Order.get_by_parent_order(order)
            if supplier_orders_qs:
                supplier = supplier_orders_qs[0].partner

        if not supplier:
            supplier = Partner.get_partner_by_taxi_id('9999999999')
            if supplier is None:
                raise Exception(
                    "No existe proveedor definifo para tarifas generales"
                )

        order_data = {
            "id": order.id,
            "serie": order.serie,
            "serie_name": "ORD-VENTA" if order.serie == "200" else "ORD-COMPRA",
            "consecutive": order.consecutive or "000000",
            "stock_day": order.stock_day.id if order.stock_day else 0,
            "date": order.date.strftime("%d/%m/%Y %H:%M") if order.date else "",
            "partner": order.partner.id,
            "type_document": order.type_document,
            "parent_order": order.parent_order.id if order.parent_order else None,
            "num_order": order.num_order,
            "delivery_date": order.delivery_date.strftime("%Y-%m-%d") if order.delivery_date else "",
            "status": order.status,
            "discount": float(order.discount),
            "total_price": float(order.total_price),
            "total_margin": float(order.total_margin),
            "comision_seler": float(order.comision_seler),
            "eb_total": order.eb_total,
            "qb_total": order.qb_total,
            "hb_total": order.hb_total,
            "fb_total": float(order.fb_total) if order.fb_total else 0,
            "total_stem_flower": order.total_stem_flower,
            "total_bunches": order.total_bunches,
            "is_invoiced": order.is_invoiced,
            "id_invoice": order.id_invoice,
            "num_invoice": order.num_invoice,
            "total_order": float(order.total_order)
        }

        if order.type_document == 'ORD_COMPRA':
            order_data["total_order"] = float(order.total_purchase_price)

            if order.parent_order:
                actual_customer_of_oc = order.parent_order.partner
                pass

        order_lines = OrderItems.get_by_order(order)
        order_lines_data = []

        for line in order_lines:
            box_items = OrderBoxItems.get_box_items(line)
            order_box_items_data = []

            for box in box_items:
                product = box.product

                box_item_data = {
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "variety": product.variety,
                        "image": product.image.url if product.image else "",
                        "colors": product.colors,
                        "default_profit_margin": str(product.default_profit_margin)
                    },
                    "length": box.length,
                    "stems_bunch": box.stems_bunch,
                    "total_bunches": box.total_bunches,
                    "qty_stem_flower": box.qty_stem_flower,
                    "stem_cost_price": str(box.stem_cost_price),
                    "profit_margin": str(box.profit_margin),
                    "total_stem_flower": box.qty_stem_flower * line.quantity,
                    "total": str(box.stem_cost_price),
                    "stem_cost_total": str(box.stem_cost_total),
                    "stem_cost_total_sale": str(box.stem_cost_total_sale),
                    "stem_cost_total_price": str(box.stem_cost_total_price),
                    "stem_cost_total_sale_with_quantity": str(box.stem_cost_total_sale_with_quantity),
                    "stem_cost_total_price_with_quantity": str(box.stem_cost_total_price_with_quantity)
                }

                order_box_items_data.append(box_item_data)

            line_data = {
                "id_stock_detail": line.id_stock_detail,
                "line_price": float(line.line_price),
                "line_margin": float(line.line_margin),
                "line_total": float(line.line_total),
                "line_commission": float(line.line_commission),
                "tot_stem_flower": line.tot_stem_flower,
                "box_model": line.box_model,
                "quantity": line.quantity,
                "order_box_items": order_box_items_data
            }

            order_lines_data.append(line_data)

        customer_data = {
            "id": customer.id,
            "name": customer.name,
            "business_tax_id": customer.business_tax_id,
            "address": customer.address,
            "country": getattr(customer, 'country', ""),
            "city": getattr(customer, 'city', ""),
            "website": customer.website,
            "credit_term": customer.credit_term,
            "consolidate": customer.consolidate,
            "skype": customer.skype,
            "email": customer.email,
            "phone": customer.phone,
            "is_active": customer.is_active,
            "contact": getattr(customer, 'contact', {}),
            "related_partners": getattr(customer, 'related_partners', []),
            "is_selected": False
        }

        current_supplier_for_main_order_view = supplier
        if order.type_document == 'ORD_COMPRA':
            current_supplier_for_main_order_view = customer

        supplier_data = {}
        if current_supplier_for_main_order_view:
            supplier_data = {
                "id": current_supplier_for_main_order_view.id,
                "name": current_supplier_for_main_order_view.name,
                "short_name": getattr(current_supplier_for_main_order_view, 'short_name', current_supplier_for_main_order_view.name),
                "business_tax_id": current_supplier_for_main_order_view.business_tax_id,
                "address": current_supplier_for_main_order_view.address,
                "country": getattr(current_supplier_for_main_order_view, 'country', ""),
                "city": getattr(current_supplier_for_main_order_view, 'city', ""),
                "website": current_supplier_for_main_order_view.website,
                "credit_term": current_supplier_for_main_order_view.credit_term,
                "is_profit_margin_included": getattr(current_supplier_for_main_order_view, 'is_profit_margin_included', False),
                "default_profit_margin": getattr(current_supplier_for_main_order_view, 'default_profit_margin', "0.06"),
                "consolidate": current_supplier_for_main_order_view.consolidate,
                "skype": current_supplier_for_main_order_view.skype,
                "email": current_supplier_for_main_order_view.email,
                "phone": current_supplier_for_main_order_view.phone,
                "is_active": current_supplier_for_main_order_view.is_active,
                "contact": getattr(current_supplier_for_main_order_view, 'contact', {}),
                "is_selected": False,
                "have_stock": getattr(current_supplier_for_main_order_view, 'have_stock', False),
                "related_partners": getattr(current_supplier_for_main_order_view, 'related_partners', [])
            }

        response_data = {
            "order": order_data,
            "orderLines": order_lines_data,
            "customer": customer_data,
            "supplier": supplier_data
        }

        purchase_orders_details = []
        if order.type_document == 'ORD_VENTA' and supplier_orders_qs:
            for sup_order_instance in supplier_orders_qs:
                sup_order_partner = sup_order_instance.partner
                sup_order_partner_data = {
                    "id": sup_order_partner.id,
                    "name": sup_order_partner.name,
                    "short_name": getattr(sup_order_partner, 'short_name', sup_order_partner.name),
                    "business_tax_id": sup_order_partner.business_tax_id,
                    "address": sup_order_partner.address,
                    "country": getattr(sup_order_partner, 'country', ""),
                    "city": getattr(sup_order_partner, 'city', ""),
                    "website": sup_order_partner.website,
                    "credit_term": sup_order_partner.credit_term,
                    "email": sup_order_partner.email,
                    "phone": sup_order_partner.phone,
                    "contact": getattr(sup_order_partner, 'contact', {}),
                    "consolidate": sup_order_partner.consolidate,
                    "skype": sup_order_partner.skype,
                }

                sup_order_data_item = {
                    "id": sup_order_instance.id,
                    "serie": sup_order_instance.serie,
                    "serie_name": "ORD-COMPRA",
                    "consecutive": sup_order_instance.consecutive or "000000",
                    "date": sup_order_instance.date.strftime("%d/%m/%Y %H:%M") if sup_order_instance.date else "",
                    "num_order": sup_order_instance.num_order,
                    "delivery_date": sup_order_instance.delivery_date.strftime("%Y-%m-%d") if sup_order_instance.delivery_date else "",
                    "status": sup_order_instance.status,
                    "total_price": float(sup_order_instance.total_price),
                    "total_order": float(sup_order_instance.total_purchase_price),
                    "eb_total": sup_order_instance.eb_total,
                    "qb_total": sup_order_instance.qb_total,
                    "hb_total": sup_order_instance.hb_total,
                    "fb_total": float(sup_order_instance.fb_total) if sup_order_instance.fb_total else 0,
                    "total_stem_flower": sup_order_instance.total_stem_flower,
                    "total_bunches": sup_order_instance.total_bunches,
                    "is_invoiced": sup_order_instance.is_invoiced,
                    "id_invoice": sup_order_instance.id_invoice,
                    "partner": sup_order_partner_data,
                }

                sup_order_lines_qs = OrderItems.get_by_order(
                    sup_order_instance)
                sup_order_lines_data_list = []
                for line in sup_order_lines_qs:
                    box_items_qs = OrderBoxItems.get_box_items(line)
                    sup_order_box_items_data_list = []
                    for box in box_items_qs:
                        product = box.product
                        sup_box_item_data = {
                            "product": {
                                "id": product.id,
                                "name": product.name,
                                "variety": product.variety,
                                "image": product.image.url if product.image else "",
                                "colors": product.colors,
                            },
                            "length": box.length,
                            "stems_bunch": box.stems_bunch,
                            "total_bunches": box.total_bunches,
                            "qty_stem_flower": box.qty_stem_flower,
                            "stem_cost_price": str(box.stem_cost_price),
                            "profit_margin": str(box.profit_margin),
                            "stem_cost_total": str(box.stem_cost_total),
                            "stem_cost_total_price_with_quantity": str(box.stem_cost_total_price_with_quantity),
                        }
                        sup_order_box_items_data_list.append(sup_box_item_data)

                    sup_line_data = {
                        "id_stock_detail": line.id_stock_detail,
                        "line_price": float(line.line_price),
                        "line_total": float(line.line_price),
                        "tot_stem_flower": line.tot_stem_flower,
                        "box_model": line.box_model,
                        "quantity": line.quantity,
                        "order_box_items": sup_order_box_items_data_list
                    }
                    sup_order_lines_data_list.append(sup_line_data)

                sup_order_data_item["orderLines"] = sup_order_lines_data_list
                purchase_orders_details.append(sup_order_data_item)

        response_data["purchase_orders_details"] = purchase_orders_details

        # Agregar información de facturas separadas por tipo
        sale_invoices_details = []
        purchase_invoices_details = []

        # Obtener facturas relacionadas con la orden principal
        if order.is_invoiced and order.id_invoice:
            try:
                main_invoice = Invoice.objects.get(
                    id=order.id_invoice, is_active=True)
                invoice_data = self._build_invoice_data(main_invoice)

                if main_invoice.type_document == 'FAC_VENTA':
                    sale_invoices_details.append(invoice_data)
                elif main_invoice.type_document == 'FAC_COMPRA':
                    purchase_invoices_details.append(invoice_data)
            except Invoice.DoesNotExist:
                pass

        # Obtener facturas de órdenes de compra relacionadas
        if order.type_document == 'ORD_VENTA' and supplier_orders_qs:
            for sup_order in supplier_orders_qs:
                if sup_order.is_invoiced and sup_order.id_invoice:
                    try:
                        sup_invoice = Invoice.objects.get(
                            id=sup_order.id_invoice, is_active=True)
                        invoice_data = self._build_invoice_data(sup_invoice)

                        if sup_invoice.type_document == 'FAC_VENTA':
                            sale_invoices_details.append(invoice_data)
                        elif sup_invoice.type_document == 'FAC_COMPRA':
                            purchase_invoices_details.append(invoice_data)
                    except Invoice.DoesNotExist:
                        pass

        # También buscar facturas que referencien esta orden directamente
        all_invoices = Invoice.objects.filter(order=order, is_active=True)
        for invoice in all_invoices:
            invoice_data = self._build_invoice_data(invoice)
            if invoice.type_document == 'FAC_VENTA':
                # Evitar duplicados
                if not any(inv['id'] == invoice.id for inv in sale_invoices_details):
                    sale_invoices_details.append(invoice_data)
            elif invoice.type_document == 'FAC_COMPRA':
                # Evitar duplicados
                if not any(inv['id'] == invoice.id for inv in purchase_invoices_details):
                    purchase_invoices_details.append(invoice_data)

        response_data["sale_invoices_details"] = sale_invoices_details
        response_data["purchase_invoices_details"] = purchase_invoices_details

        context['response_data'] = response_data

        context['customer'] = customer
        context['supplier'] = supplier
        context['order_lines'] = order_lines_data
        context['delivery_date'] = order.delivery_date
        context['status'] = order.status
        context['order'] = order
        context['total_price'] = order.total_price
        context['total_margin'] = order.total_margin
        context['total_invoice'] = order.total_price + order.total_margin
        context['hb_total'] = order.hb_total
        context['qb_total'] = order.qb_total
        context['fb_total'] = order.fb_total
        context['total_stem_flower'] = order.total_stem_flower
        context['total_bunches'] = order.total_bunches

        context['action'] = self.request.GET.get('action')

        if 'action' in self.request.GET:
            context['action_type'] = self.request.GET.get('action')
            message = ''

            if context['action'] == 'created':
                message = 'La orden ha sido creada con éxito.'
            elif context['action'] == 'updated':
                message = 'La orden ha sido actualizada con éxito.'
            elif context['action'] == 'confirmed':
                message = 'La orden ha sido confirmada con éxito.'
            elif context['action'] == 'delete':
                message = 'Esta acción es irreversible. ¿Desea continuar?.'
            elif context['action'] == 'deleted_related':
                message = 'El registro ha sido eliminado exitosamente.'

            context['message'] = message

        # Agregar información sobre si la orden puede ser confirmada
        context['can_confirm'] = order.status in [
            'PENDIENTE', 'MODIFICADO'] and not order.is_invoiced

        return context

    def _build_invoice_data(self, invoice):
        """Construir datos de factura para el contexto"""
        invoice_items = InvoiceItems.get_invoice_items(invoice)
        invoice_lines_data = []

        for line in invoice_items:
            box_items = InvoiceBoxItems.get_box_items(line)
            invoice_box_items_data = []

            for box in box_items:
                product = box.product
                box_item_data = {
                    "product": {
                        "id": product.id,
                        "name": product.name,
                        "variety": product.variety,
                        "image": product.image.url if product.image else "",
                        "colors": product.colors,
                    },
                    "length": box.length,
                    "stems_bunch": box.stems_bunch,
                    "total_bunches": box.total_bunches,
                    "qty_stem_flower": box.qty_stem_flower,
                    "stem_cost_price": str(box.stem_cost_price),
                    "profit_margin": str(box.profit_margin),
                    "total_price": str(box.total_price),
                    "unit_price": str(box.unit_price),
                    "total_price_with_margin": str(box.total_price_with_margin),
                }
                invoice_box_items_data.append(box_item_data)

            line_data = {
                "id": line.id,
                "line_price": float(line.line_price),
                "line_margin": float(line.line_margin),
                "line_total": float(line.line_total),
                "tot_stem_flower": line.tot_stem_flower,
                "total_bunches": line.total_bunches,
                "box_model": line.box_model,
                "quantity": line.quantity,
                "invoice_box_items": invoice_box_items_data
            }
            invoice_lines_data.append(line_data)

        invoice_data = {
            "id": invoice.id,
            "serie": invoice.serie,
            "consecutive": invoice.consecutive,
            "num_invoice": invoice.num_invoice,
            "type_document": invoice.type_document,
            "date": invoice.date.strftime("%d/%m/%Y %H:%M") if invoice.date else "",
            "due_date": invoice.due_date.strftime("%d/%m/%Y") if invoice.due_date else "",
            "status": invoice.status,
            "total_price": float(invoice.total_price),
            "total_margin": float(invoice.total_margin),
            "total_invoice": float(invoice.total_invoice),
            "eb_total": invoice.eb_total,
            "qb_total": invoice.qb_total,
            "hb_total": invoice.hb_total,
            "fb_total": float(invoice.fb_total) if invoice.fb_total else 0,
            "tot_stem_flower": invoice.tot_stem_flower,
            "total_bunches": invoice.total_bunches,
            "awb": invoice.awb,
            "hawb": invoice.hawb,
            "dae_export": invoice.dae_export,
            "cargo_agency": invoice.cargo_agency,
            "delivery_date": invoice.delivery_date.strftime("%Y-%m-%d") if invoice.delivery_date else "",
            "weight": str(invoice.weight) if invoice.weight else "",
            "days_to_due": invoice.days_to_due,
            "is_dued": invoice.is_dued,
            "days_overdue": invoice.days_overdue,
            "partner": {
                "id": invoice.partner.id,
                "name": invoice.partner.name,
                "business_tax_id": invoice.partner.business_tax_id,
                "address": invoice.partner.address,
                "country": getattr(invoice.partner, 'country', ""),
                "city": getattr(invoice.partner, 'city', ""),
                "email": invoice.partner.email,
                "phone": invoice.partner.phone,
                "credit_term": invoice.partner.credit_term,
            },
            "order_id": invoice.order.id,
            "invoiceLines": invoice_lines_data
        }

        return invoice_data
