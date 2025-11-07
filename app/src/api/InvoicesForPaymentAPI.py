from django.http import JsonResponse
from django.views import View
from common.InvoiceBalance import InvoiceBalance
from trade.models import Invoice
from decimal import Decimal


class InvoicesForPaymentAPI(View):
    def get(self, request):
        """Obtiene todas las facturas pendientes con sus saldos actualizados"""
        partner_id = request.GET.get('partner_id')
        
        # Obtener facturas con saldo pendiente (incluyendo las que tienen pagos anulados)
        # Solo facturas activas (is_active=True)
        invoices_data = InvoiceBalance.get_pending_invoices(partner_id=partner_id)
        
        # Formatear datos para el frontend
        invoices_list = []
        for invoice_data in invoices_data:
            invoice = invoice_data['invoice']
            
            # Validar que la factura y el partner estén activos
            if not invoice.is_active or not invoice.partner.is_active:
                continue
            
            invoices_list.append({
                'id': invoice.id,
                'serie': invoice.serie or '000',
                'consecutive': invoice.consecutive,
                'num_invoice': invoice.num_invoice,
                'partner_id': invoice.partner.id,
                'partner_name': invoice.partner.name,
                'date': invoice.date.isoformat() if invoice.date else None,
                'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
                'total_amount': float(invoice_data['total_amount']),
                'paid_amount': float(invoice_data['paid_amount']),
                'balance': float(invoice_data['balance']),
                'status': invoice_data['status'],
                'days_overdue': invoice.days_overdue,
                'is_overdue': invoice.is_dued,
            })
        
        # Calcular estadísticas
        total_pending = sum(inv['balance'] for inv in invoices_list)
        overdue_invoices = [inv for inv in invoices_list if inv['is_overdue']]
        total_overdue = sum(inv['balance'] for inv in overdue_invoices)
        
        # Facturas que vencen en los próximos 7 días
        upcoming_due = []
        for inv in invoices_list:
            if not inv['is_overdue'] and inv.get('days_overdue') is not None:
                days_to_due = abs(inv['days_overdue'])
                if days_to_due <= 7:
                    upcoming_due.append(inv)
        
        total_upcoming = sum(inv['balance'] for inv in upcoming_due)
        
        return JsonResponse({
            'invoices': invoices_list,
            'statistics': {
                'pending_invoices': {
                    'count': len(invoices_list),
                    'total_amount': float(total_pending)
                },
                'overdue_payments': {
                    'count': len(overdue_invoices),
                    'total_amount': float(total_overdue)
                },
                'upcoming_due_invoices': {
                    'count': len(upcoming_due),
                    'total_amount': float(total_upcoming)
                }
            }
        })

    def post(self, request, *args, **kwargs):
        """
        Obtiene facturas que vencen en un rango de fechas específico
        """
        try:
            import json
            from datetime import datetime

            data = json.loads(request.body)
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            document_type = data.get('type', None)

            if not start_date or not end_date:
                return JsonResponse({
                    'success': False,
                    'error': 'start_date y end_date son requeridos'
                }, status=400)

            # Validar tipo de documento si se proporciona
            if document_type and document_type not in ['FAC_VENTA', 'FAC_COMPRA']:
                return JsonResponse({
                    'success': False,
                    'error': 'Tipo de documento inválido. Use FAC_VENTA o FAC_COMPRA'
                }, status=400)

            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de fecha inválido. Use YYYY-MM-DD'
                }, status=400)

            if start_date > end_date:
                return JsonResponse({
                    'success': False,
                    'error': 'start_date no puede ser mayor que end_date'
                }, status=400)

            # Crear instancia y obtener facturas en el rango
            invoices_manager = InvoicesPaymentPending(
                type_document=document_type)
            invoices_data = invoices_manager.get_invoices_due_in_range(
                start_date, end_date)

            return JsonResponse({
                'success': True,
                'data': {
                    'invoices_due_in_range': invoices_data,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'type_document': document_type,
                    'total_invoices': len(invoices_data),
                    'total_amount': sum(inv['balance_due'] for inv in invoices_data)
                }
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'JSON inválido en el cuerpo de la petición'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Error interno del servidor: {str(e)}'
            }, status=500)
