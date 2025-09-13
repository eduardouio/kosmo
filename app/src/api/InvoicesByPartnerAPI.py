from django.http import JsonResponse
from django.views import View
from django.db.models import Sum
from trade.models.Invoice import Invoice
from trade.models.Payment import PaymentDetail


class InvoicesByPartnerAPI(View):
    """
    API para obtener facturas pendientes de pago por cliente
    """

    def get(self, request):
        partner_id = request.GET.get('partner_id')

        if not partner_id:
            return JsonResponse({
                'success': False,
                'error': 'partner_id es requerido'
            })

        try:
            # Obtener facturas del cliente que no estén anuladas
            invoices = Invoice.objects.filter(
                partner_id=partner_id,
                is_active=True
            ).exclude(
                status='ANULADO'
            ).select_related('order')

            invoices_data = []

            for invoice in invoices:
                # Calcular pagos aplicados a esta factura
                paid_amount = PaymentDetail.objects.filter(
                    invoice=invoice,
                    payment__status='CONFIRMADO',
                    payment__is_active=True
                ).aggregate(
                    total=Sum('amount')
                )['total'] or 0

                # Calcular saldo pendiente
                pending_balance = invoice.total_price - paid_amount

                # Solo incluir facturas con saldo pendiente
                if pending_balance > 0:
                    # Formatear número de factura con serie-consecutivo
                    serie = invoice.serie or '000'
                    consecutive = str(invoice.consecutive or '0').zfill(7)
                    display_number = f"{serie}-{consecutive}"
                    
                    # Agregar número de pedido si existe
                    if invoice.order and invoice.order.num_order:
                        order_num = invoice.order.num_order
                        display_number += f" (Pedido: {order_num})"

                    date_str = ''
                    if invoice.date:
                        date_str = invoice.date.strftime('%Y-%m-%d')

                    order_number = ''
                    if invoice.order:
                        order_number = invoice.order.num_order

                    invoices_data.append({
                        'id': invoice.id,
                        'display_number': display_number,
                        'num_invoice': invoice.num_invoice,
                        'serie': serie,
                        'consecutive': consecutive,
                        'total_price': float(invoice.total_price),
                        'paid_amount': float(paid_amount),
                        'pending_balance': float(pending_balance),
                        'date': date_str,
                        'order_number': order_number
                    })

            return JsonResponse({
                'success': True,
                'invoices': invoices_data
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })