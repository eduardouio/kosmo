from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event
from common import CreateInvoiceByOrder
from datetime import datetime, timedelta


class BatchOrderApprovalView(View):
    """
    Vista para aprobar múltiples órdenes de venta en lote y generar facturas
    """

    def post(self, request, *args, **kwargs):
        try:
            order_ids = request.POST.getlist('order_ids[]')

            if not order_ids:
                return JsonResponse({
                    'success': False,
                    'message': 'No se recibieron órdenes para aprobar'
                }, status=400)

            try:
                order_ids = [int(order_id) for order_id in order_ids]
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'IDs de órdenes inválidos'
                }, status=400)

            orders_to_approve = Order.objects.filter(
                id__in=order_ids,
                type_document='ORD_VENTA',
                status__in=['PENDIENTE', 'MODIFICADO', 'PROMESA'],
                is_active=True
            )

            if not orders_to_approve.exists():
                return JsonResponse({
                    'success': False,
                    'message': 'No se encontraron órdenes válidas para aprobar'
                }, status=400)

            approved_count = 0
            invoiced_count = 0
            errors = []

            for order in orders_to_approve:
                try:
                    # Paso 1: Cambiar estado a CONFIRMADO
                    old_status = order.status
                    order.status = 'CONFIRMADO'
                    order.save()

                    loggin_event(
                        f"Orden {order.id} confirmada por lotes. "
                        f"Estado anterior: {old_status}, Estado actual: CONFIRMADO. "
                        f"Usuario: {request.user}"
                    )

                    # Confirmar órdenes de compra relacionadas si existen
                    self.approve_related_purchase_orders(order)

                    approved_count += 1

                    # Paso 2: Generar factura y cambiar estado a FACTURADO
                    try:
                        invoice = CreateInvoiceByOrder().generate_invoice(order)
                        
                        # Crear facturas de compra automáticamente
                        self.create_purchase_invoices(order)
                        
                        invoiced_count += 1
                        
                        loggin_event(
                            f"Factura generada para orden {order.id}: {invoice.num_invoice}. "
                            f"Usuario: {request.user}"
                        )
                        
                    except Exception as e:
                        error_msg = f"Error al generar factura para orden {order.id}: {str(e)}"
                        errors.append(error_msg)
                        loggin_event(error_msg, error=True)

                except Exception as e:
                    error_msg = f"Error al procesar orden {order.id}: {str(e)}"
                    errors.append(error_msg)
                    loggin_event(error_msg, error=True)

            # Preparar respuesta
            if approved_count > 0:
                success_message = f"Se procesaron exitosamente {approved_count} órdenes"
                if invoiced_count > 0:
                    success_message += f" y se generaron {invoiced_count} facturas"
                
                if errors:
                    success_message += f". {len(errors)} órdenes tuvieron errores"

                loggin_event(
                    f"Proceso de aprobación y facturación por lotes completado. "
                    f"Confirmadas: {approved_count}, Facturadas: {invoiced_count}, "
                    f"Errores: {len(errors)}. Usuario: {request.user}"
                )

                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'approved_count': approved_count,
                    'invoiced_count': invoiced_count,
                    'errors': errors
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo procesar ninguna orden',
                    'errors': errors
                }, status=400)

        except Exception as e:
            error_msg = f"Error general en procesamiento por lotes: {str(e)}"
            loggin_event(error_msg, error=True)

            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    def approve_related_purchase_orders(self, sale_order):
        """Aprobar órdenes de compra relacionadas con la orden de venta"""
        try:
            purchase_orders = Order.get_by_parent_order(sale_order)
            if purchase_orders:
                for purchase_order in purchase_orders:
                    if purchase_order.status in ['PENDIENTE', 'MODIFICADO', 'PROMESA']:
                        purchase_order.status = 'CONFIRMADO'
                        purchase_order.save()
                        loggin_event(
                            f"Orden de compra {purchase_order.id} confirmada "
                            f"automáticamente por orden de venta {sale_order.id}"
                        )
        except Exception as e:
            loggin_event(f"Error al confirmar órdenes de compra relacionadas: {str(e)}", error=True)

    def create_purchase_invoices(self, sale_order):
        """Crear facturas de compra para todas las órdenes de compra relacionadas"""
        from trade.models import Invoice, InvoiceItems, InvoiceBoxItems, OrderItems, OrderBoxItems
        
        try:
            loggin_event(f'Creando facturas de compra para orden de venta {sale_order.id}')
            
            # Obtener órdenes de compra relacionadas
            purchase_orders = Order.get_by_parent_order(sale_order)
            
            if not purchase_orders:
                loggin_event('No hay órdenes de compra para facturar')
                return
            
            for purchase_order in purchase_orders:
                if purchase_order.is_invoiced:
                    loggin_event(f'Orden de compra {purchase_order.id} ya está facturada')
                    continue
                    
                loggin_event(f'Creando factura para orden de compra {purchase_order.id}')
                
                # Calcular fecha de vencimiento
                days = purchase_order.partner.credit_term if purchase_order.partner.credit_term else 30
                due_date = datetime.now() + timedelta(days=days)
                
                # Crear número de factura con formato SinFact-{serie-consecutivo}
                num_invoice = f"SinFact-{purchase_order.serie or '200'}-{str(purchase_order.consecutive or 0).zfill(6)}"
                
                # Crear factura de compra
                purchase_invoice = Invoice.objects.create(
                    order=purchase_order,
                    partner=purchase_order.partner,
                    type_document='FAC_COMPRA',
                    date=datetime.now(),
                    due_date=due_date,
                    status='PENDIENTE',
                    num_invoice=num_invoice,
                    serie='',
                    consecutive=None,
                    total_price=purchase_order.total_price,
                    total_margin=0,
                    qb_total=purchase_order.qb_total,
                    hb_total=purchase_order.hb_total,
                    fb_total=purchase_order.fb_total,
                    tot_stem_flower=purchase_order.total_stem_flower,
                    total_bunches=purchase_order.total_bunches
                )
                
                # Copiar items de la orden a la factura
                self.copy_order_items_to_invoice(purchase_order, purchase_invoice)
                
                # Actualizar orden de compra
                purchase_order.status = 'FACTURADO'
                purchase_order.is_invoiced = True
                purchase_order.id_invoice = purchase_invoice.id
                purchase_order.num_invoice = purchase_invoice.num_invoice
                purchase_order.save()
                
                loggin_event(f'Factura de compra creada: {purchase_invoice.num_invoice}')
                
        except Exception as e:
            loggin_event(f"Error al crear facturas de compra: {str(e)}", error=True)

    def copy_order_items_to_invoice(self, order, invoice):
        """Copiar items de la orden a la factura"""
        from trade.models import InvoiceItems, InvoiceBoxItems, OrderItems, OrderBoxItems
        
        try:
            order_items = OrderItems.get_by_order(order)
            
            for order_item in order_items:
                # Crear item de factura
                invoice_item = InvoiceItems.objects.create(
                    invoice=invoice,
                    id_stock_detail=order_item.id_stock_detail,
                    line_price=order_item.line_price,
                    line_margin=order_item.line_margin,
                    line_total=order_item.line_total,
                    line_commission=order_item.line_commission,
                    tot_stem_flower=order_item.tot_stem_flower
                )
                
                # Copiar box items
                order_box_items = OrderBoxItems.get_by_order_item(order_item)
                for box_item in order_box_items:
                    InvoiceBoxItems.objects.create(
                        invoice_item=invoice_item,
                        type_box=box_item.type_box,
                        quantity=box_item.quantity,
                        price=box_item.price,
                        total=box_item.total,
                        tot_stem_flower=box_item.tot_stem_flower
                    )
                    
        except Exception as e:
            loggin_event(f"Error al copiar items de orden a factura: {str(e)}", error=True)

    def get(self, request, *args, **kwargs):
        """
        Manejar solicitudes GET redirigiendo a la lista de órdenes
        """
        messages.warning(request, 'Método no permitido para esta operación')
        return redirect('customer_orders_list')
