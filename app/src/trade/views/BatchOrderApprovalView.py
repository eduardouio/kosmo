from django.views.generic import View
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from trade.models import Order
from common.AppLoger import loggin_event


class BatchOrderApprovalView(View):
    """
    Vista para aprobar múltiples órdenes de venta en lote
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
            errors = []

            for order in orders_to_approve:
                try:
                    old_status = order.status
                    order.status = 'CONFIRMADO'
                    order.save()

                    loggin_event(
                        f"Orden {order.id} aprobada por lotes. "
                        f"Estado anterior: {old_status}, Estado actual: CONFIRMADO. "
                        f"Usuario: {request.user}"
                    )

                    approved_count += 1

                except Exception as e:
                    error_msg = f"Error al aprobar orden {order.id}: {str(e)}"
                    errors.append(error_msg)
                    loggin_event(error_msg, error=True)

            if approved_count > 0:
                success_message = f"Se aprobaron exitosamente {approved_count} órdenes"

                if errors:
                    success_message += f". {len(errors)} órdenes tuvieron errores"

                loggin_event(
                    f"Proceso de aprobación por lotes completado. "
                    f"Aprobadas: {approved_count}, Errores: {len(errors)}. "
                    f"Usuario: {request.user}"
                )

                return JsonResponse({
                    'success': True,
                    'message': success_message,
                    'approved_count': approved_count,
                    'errors': errors
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'No se pudo aprobar ninguna orden',
                    'errors': errors
                }, status=400)

        except Exception as e:
            error_msg = f"Error general en aprobación por lotes: {str(e)}"
            loggin_event(error_msg, error=True)

            return JsonResponse({
                'success': False,
                'message': 'Error interno del servidor'
            }, status=500)

    def get(self, request, *args, **kwargs):
        """
        Manejar solicitudes GET redirigiendo a la lista de órdenes
        """
        messages.warning(request, 'Método no permitido para esta operación')
        return redirect('customer_orders_list')
