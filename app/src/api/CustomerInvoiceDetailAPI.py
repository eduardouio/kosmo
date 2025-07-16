from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trade.models.Invoice import Invoice, InvoiceItems, InvoiceBoxItems
from partners.models import Partner
from products.models import Product
from django.shortcuts import get_object_or_404


class CustomerInvoiceDetailAPI(APIView):
    """
    API para obtener detalles completos de una factura
    """

    def get(self, request, invoice_id):
        """
        Obtiene detalles completos de una factura por el ID de la factura
        """
        # Buscar la factura por el invoice_id
        invoice = get_object_or_404(Invoice, id=invoice_id, is_active=True)

        # Obtener el cliente y proveedor
        customer = invoice.partner
        supplier = None

        # Si es una factura de venta, buscar la orden de compra relacionada para obtener proveedor
        if invoice.type_document == 'FAC_VENTA' and invoice.order:
            from trade.models.Order import Order
            supplier_orders = Order.get_by_parent_order(invoice.order)
            if supplier_orders:
                supplier = supplier_orders[0].partner

        # Si no se encontró proveedor, usar uno por defecto
        if not supplier:
            supplier = Partner.get_partner_by_taxi_id('9999999999')
            if supplier is None:
                raise Exception(
                    "No existe proveedor definido para tarifas generales"
                )

        # Construir respuesta JSON para la factura
        invoice_data = {
            "id": invoice.id,
            "serie": invoice.serie,
            "consecutive": f"{invoice.consecutive:06d}",
            "marking": invoice.marking,
            "date": invoice.date.strftime("%Y-%m-%d") if invoice.date else "",
            "due_date": invoice.due_date.strftime("%Y-%m-%d") if invoice.due_date else "",
            "partner": invoice.partner.id,
            "type_document": invoice.type_document,
            "order_id": invoice.order.id if invoice.order else None,
            "num_invoice": invoice.num_invoice,
            "status": invoice.status,
            "total_price": float(invoice.total_price),
            "total_margin": float(invoice.total_margin),
            "comision_seler": float(invoice.comision_seler),
            "qb_total": invoice.qb_total,
            "hb_total": invoice.hb_total,
            "eb_total": invoice.eb_total,
            "fb_total": float(invoice.fb_total),
            "total_pieces": invoice.total_pieces,
            "tot_stem_flower": invoice.tot_stem_flower,
            "total_bunches": invoice.total_bunches,
            "po_number": invoice.po_number,
            "awb": invoice.awb,
            "dae_export": invoice.dae_export,
            "hawb": invoice.hawb,
            "cargo_agency": invoice.cargo_agency,
            "delivery_date": invoice.delivery_date.strftime("%Y-%m-%d") if invoice.delivery_date else "",
            "weight": float(invoice.weight) if invoice.weight else 0.0,
            # Campos de BaseModel
            "notes": invoice.notes,
            "created_at": invoice.created_at.strftime("%Y-%m-%d %H:%M:%S") if invoice.created_at else "",
            "updated_at": invoice.updated_at.strftime("%Y-%m-%d %H:%M:%S") if invoice.updated_at else "",
            "is_active": invoice.is_active,
            "id_user_created": invoice.id_user_created,
            "id_user_updated": invoice.id_user_updated
        }

        # Obtener líneas de factura
        invoice_lines = InvoiceItems.get_invoice_items(invoice)
        invoice_lines_data = []

        for line in invoice_lines:
            box_items = InvoiceBoxItems.get_box_items(line)
            invoice_box_items_data = []

            for box in box_items:
                product = box.product

                box_item_data = {
                    "id": box.id,
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
                    "commission": str(box.commission),
                    "total_stem_flower": box.qty_stem_flower * line.quantity,
                    "total": str(box.stem_cost_price),
                    # Campos de BaseModel
                    "notes": box.notes,
                    "created_at": box.created_at.strftime("%Y-%m-%d %H:%M:%S") if box.created_at else "",
                    "updated_at": box.updated_at.strftime("%Y-%m-%d %H:%M:%S") if box.updated_at else "",
                    "is_active": box.is_active,
                    "id_user_created": box.id_user_created,
                    "id_user_updated": box.id_user_updated
                }

                invoice_box_items_data.append(box_item_data)

            line_data = {
                "id": line.id,
                "id_order_item": line.id_order_item,
                "line_price": float(line.line_price),
                "line_margin": float(line.line_margin),
                "line_total": float(line.line_total),
                "line_commission": float(line.line_commission),
                "tot_stem_flower": line.tot_stem_flower,
                "box_model": line.box_model,
                "quantity": line.quantity,
                "total_bunches": line.total_bunches,
                "invoice_box_items": invoice_box_items_data,
                # Campos de BaseModel
                "notes": line.notes,
                "created_at": line.created_at.strftime("%Y-%m-%d %H:%M:%S") if line.created_at else "",
                "updated_at": line.updated_at.strftime("%Y-%m-%d %H:%M:%S") if line.updated_at else "",
                "is_active": line.is_active,
                "id_user_created": line.id_user_created,
                "id_user_updated": line.id_user_updated
            }

            invoice_lines_data.append(line_data)

        # Construir respuesta JSON para el cliente
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

        # Construir respuesta JSON para el proveedor
        supplier_data = {
            "id": supplier.id,
            "name": supplier.name,
            "short_name": getattr(supplier, 'short_name', supplier.name),
            "business_tax_id": supplier.business_tax_id,
            "address": supplier.address,
            "city": getattr(supplier, 'city', ""),
            "website": supplier.website,
            "credit_term": supplier.credit_term,
            "is_profit_margin_included": getattr(supplier, 'is_profit_margin_included', False),
            "default_profit_margin": getattr(supplier, 'default_profit_margin', "0.06"),
            "consolidate": supplier.consolidate,
            "skype": supplier.skype,
            "email": supplier.email,
            "phone": supplier.phone,
            "is_active": supplier.is_active,
            "contact": getattr(supplier, 'contact', {}),
            "is_selected": False,
            "have_stock": getattr(supplier, 'have_stock', False),
            "related_partners": getattr(supplier, 'related_partners', [])
        }

        # Construir respuesta JSON completa
        response_data = {
            "invoice": invoice_data,
            "invoiceLines": invoice_lines_data,
            "customer": customer_data,
            "supplier": supplier_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
