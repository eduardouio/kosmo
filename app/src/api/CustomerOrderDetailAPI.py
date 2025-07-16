from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from trade.models.Order import Order, OrderItems, OrderBoxItems
from partners.models import Partner
from products.models import Product
from django.shortcuts import get_object_or_404


class CustomerOrderDetailAPI(APIView):
    """
    API para obtener detalles completos de un pedido
    """

    def get(self, request, order_id):
        """
        Obtiene detalles completos de un pedido por su ID
        """
        order = get_object_or_404(Order, pk=order_id)

        # Obtener el cliente y proveedor
        customer = order.partner
        supplier = None

        # Si es una orden de venta, buscar la orden de compra relacionada para obtener proveedor
        if order.type_document == 'ORD_VENTA' and Order.get_by_parent_order(order):
            supplier_orders = Order.get_by_parent_order(order)
            if supplier_orders:
                supplier = supplier_orders[0].partner

        # Si no se encontró proveedor, usar uno por defecto
        if not supplier:
            supplier = Partner.get_partner_by_taxi_id('9999999999')
            if supplier is None:
                raise Exception(
                    "No existe proveedor definifo para tarifas generales"
                )

        # Construir respuesta JSON para el pedido
        order_data = {
            "serie": order.serie,
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
            "total_order": float(order.total_order),
            "comision_seler": float(order.comision_seler),
            "qb_total": order.qb_total,
            "hb_total": order.hb_total,
            "fb_total": float(order.fb_total) if order.fb_total else 0,
            "total_stem_flower": order.total_stem_flower,
            "is_invoiced": order.is_invoiced,
            "id_invoice": order.id_invoice,
            "num_invoice": order.num_invoice
        }

        # Obtener líneas de pedido
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
                    "total": str(box.stem_cost_price)
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
            "order": order_data,
            "orderLines": order_lines_data,
            "customer": customer_data,
            "supplier": supplier_data
        }

        return Response(response_data, status=status.HTTP_200_OK)
