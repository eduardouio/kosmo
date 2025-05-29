from django.http import JsonResponse
from django.views import View
from common.InvoicesPaymentPending import (
    InvoicesPaymentPending,
    get_sales_pending_invoices,
    get_purchase_pending_invoices,
    get_all_pending_invoices
)


class InvoicesForPaymentAPI(View):

    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('type', 'all')
        partner_id = request.GET.get('partner_id', None)
        overdue_only = request.GET.get(
            'overdue_only', 'false').lower() == 'true'

        if report_type == 'sales':
            if partner_id or overdue_only:
                invoices_manager = InvoicesPaymentPending(
                    type_document='FAC_VENTA')
                if partner_id:
                    partner_id = int(partner_id)
                    invoices_data = invoices_manager.get_customer_pending_invoices(
                        partner_id)
                    if overdue_only:
                        invoices_data = [
                            inv for inv in invoices_data if inv['is_overdue']]
                elif overdue_only:
                    invoices_data = invoices_manager.get_overdue_invoices()
            else:
                invoices_data = get_sales_pending_invoices()

        elif report_type == 'purchase':
            if partner_id or overdue_only:
                invoices_manager = InvoicesPaymentPending(
                    type_document='FAC_COMPRA')
                if partner_id:
                    partner_id = int(partner_id)
                    invoices_data = invoices_manager.get_customer_pending_invoices(
                        partner_id)
                    if overdue_only:
                        invoices_data = [
                            inv for inv in invoices_data if inv['is_overdue']]
                elif overdue_only:
                    invoices_data = invoices_manager.get_overdue_invoices()
            else:
                invoices_data = get_purchase_pending_invoices()
        else:
            if partner_id or overdue_only:
                invoices_manager = InvoicesPaymentPending()
                if partner_id:
                    partner_id = int(partner_id)
                    invoices_data = invoices_manager.get_customer_pending_invoices(
                        partner_id)
                    if overdue_only:
                        invoices_data = [
                            inv for inv in invoices_data if inv['is_overdue']]
                elif overdue_only:
                    invoices_data = invoices_manager.get_overdue_invoices()
            else:
                invoices_data = get_all_pending_invoices()

        return JsonResponse({
            'success': True,
            'data': invoices_data
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
