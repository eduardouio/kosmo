import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.conf import settings

from trade.models import Payment, PaymentDetail, Invoice
from common.AppLoger import loggin_event


class PaymentCreateUpdateAPI(View):

    def post(self, request):
        """Crear un nuevo pago"""
        loggin_event('Creando nuevo pago')

        # Determinar si los datos vienen como FormData (con archivos) o JSON
        if (
            request.content_type and
            'multipart/form-data' in request.content_type
        ):
            # Datos con archivo - usar request.POST y request.FILES
            payment_data = dict(request.POST)

            # Convertir listas de un elemento a valores únicos
            for key, value in payment_data.items():
                if isinstance(value, list) and len(value) == 1:
                    payment_data[key] = value[0]

            # Procesar las facturas que vienen como JSON string
            if 'invoices' in payment_data:
                try:
                    payment_data['invoices'] = json.loads(
                        payment_data['invoices'])
                except json.JSONDecodeError:
                    return JsonResponse(
                        {'error': 'Invalid invoices data format'},
                        status=400
                    )

            # Obtener el archivo adjunto si existe
            document_file = request.FILES.get('document')
        else:
            # Datos JSON tradicionales
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)
            try:
                payment_data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

            document_file = None

        if not payment_data:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Validar campos requeridos
        required_fields = ['date', 'amount', 'method', 'invoices']
        for field in required_fields:
            if field not in payment_data:
                return JsonResponse(
                    {'error': f'Missing required field: {field}'},
                    status=400
                )

        # Validar que haya al menos una factura
        if not payment_data['invoices'] or len(payment_data['invoices']) == 0:
            return JsonResponse(
                {'error': 'At least one invoice is required'},
                status=400
            )

        with transaction.atomic():
            # Helper para formatear errores de validación
            def map_validation_errors(error: ValidationError):
                errors = {}
                msg_dict = getattr(error, 'message_dict', None) or {}
                # Si vienen errores por campo, usarlos
                for key, val in msg_dict.items():
                    if key in ['nro_operation', 'reference']:
                        errors['reference'] = (
                            val[0] if isinstance(val, list) else val
                        )
                    elif key == 'bank':
                        errors['bank'] = (
                            val[0] if isinstance(val, list) else val
                        )
                    else:
                        errors[key] = val

                # Si es un error general (__all__), mapear por contenido
                all_msgs = msg_dict.get('__all__') if msg_dict else None
                if not errors and all_msgs:
                    for msg in all_msgs:
                        lower = str(msg).lower()
                        if 'operaci' in lower:
                            errors['reference'] = msg
                        elif 'banco' in lower:
                            errors['bank'] = msg
                        else:
                            errors.setdefault('__all__', []).append(msg)

                # Si no había message_dict, usar e.messages
                if not errors and getattr(error, 'messages', None):
                    for msg in error.messages:
                        lower = str(msg).lower()
                        if 'operaci' in lower:
                            errors['reference'] = msg
                        elif 'banco' in lower:
                            errors['bank'] = msg
                        else:
                            errors.setdefault('__all__', []).append(msg)

                return errors or {'__all__': ['Error de validación']}
            # Obtener configuración bancaria por defecto
            bank_config = settings.BANK_ACCOUNT

            # Crear el pago principal
            payment = Payment(
                date=payment_data['date'],
                due_date=payment_data.get('due_date'),
                type_transaction=payment_data.get(
                    'type_transaction', 'EGRESO'),
                amount=Decimal(str(payment_data['amount'])),
                method=payment_data['method'],
                status=payment_data.get('status', 'CONFIRMADO'),
                bank=payment_data.get(
                    'bank', bank_config.get('bank_name', '')),
                nro_account=payment_data.get(
                    'nro_account', bank_config.get('account_number', '')),
                nro_operation=payment_data.get('nro_operation'),
                notes=payment_data.get('notes') or None,
                processed_by_id=payment_data.get('processed_by_id'),
                approved_by_id=payment_data.get('approved_by_id'),
                approval_date=payment_data.get('approval_date')
            )

            # Asignar el documento adjunto si existe
            if document_file:
                payment.document = document_file

            # Generar número de pago automáticamente
            payment.payment_number = Payment.get_next_payment_number()

            # Validar el pago antes de guardar
            try:
                payment.full_clean()
            except ValidationError as e:
                return JsonResponse(
                    {'errors': map_validation_errors(e)},
                    status=400
                )
            payment.save()

            # Crear los detalles de pago para cada factura
            total_invoice_amount = Decimal('0')
            for invoice_data in payment_data['invoices']:
                if (
                    'invoice_id' not in invoice_data or
                    'amount' not in invoice_data
                ):
                    raise ValidationError(
                        'Each invoice must have invoice_id and amount'
                    )

                invoice = Invoice.objects.get(id=invoice_data['invoice_id'])

                payment_detail = PaymentDetail(
                    payment=payment,
                    invoice=invoice,
                    amount=Decimal(str(invoice_data['amount']))
                )

                # Validar el detalle de pago
                try:
                    payment_detail.full_clean()
                except ValidationError as e:
                    return JsonResponse(
                        {'errors': map_validation_errors(e)},
                        status=400
                    )
                payment_detail.save()

                total_invoice_amount += payment_detail.amount

            # Validar que el monto total del pago coincida
            # con la suma de los detalles
            if payment.amount != total_invoice_amount:
                return JsonResponse(
                    {
                        'errors': {
                            '__all__': [
                                (
                                    'El monto del pago no coincide con la '
                                    'suma de los montos por factura'
                                )
                            ]
                        }
                    },
                    status=400
                )

            loggin_event(
                f'Pago creado exitosamente: {payment.payment_number}')

            # Devolver información completa del pago creado
            return JsonResponse({
                'message': 'Payment created successfully',
                'payment': {
                    'id': payment.id,
                    'payment_number': payment.payment_number,
                    'date': payment.date.isoformat() if payment.date else None,
                    'amount': str(payment.amount),
                    'method': payment.method,
                    'status': payment.status,
                    'bank': payment.bank,
                    'nro_account': payment.nro_account,
                    'nro_operation': payment.nro_operation
                }
            }, status=201)

    def get(self, request, payment_id=None):
        """Obtener información básica de un pago (solo para visualización)"""
        if payment_id:
            # Solo devolver información básica, no para edición
            try:
                payment = Payment.objects.get(id=payment_id)

                payment_data = {
                    'id': payment.id,
                    'payment_number': payment.payment_number,
                    'date': payment.date.isoformat() if payment.date else None,
                    'amount': str(payment.amount),
                    'method': payment.method,
                    'status': payment.status,
                    'bank': payment.bank
                }

                return JsonResponse(payment_data, status=200)

            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment not found'}, status=404)
        else:
            return JsonResponse({'error': 'Payment ID required'}, status=400)
