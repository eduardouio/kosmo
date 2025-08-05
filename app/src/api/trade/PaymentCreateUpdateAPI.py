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

        if not request.body:
            return JsonResponse({'error': 'No data provided'}, status=400)
        payment_data = json.loads(request.body)

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
                processed_by_id=payment_data.get('processed_by_id'),
                approved_by_id=payment_data.get('approved_by_id'),
                approval_date=payment_data.get('approval_date')
            )

            # Generar número de pago automáticamente
            payment.payment_number = Payment.get_next_payment_number()

            # Validar el pago antes de guardar
            payment.full_clean()
            payment.save()

            # Crear los detalles de pago para cada factura
            total_invoice_amount = Decimal('0')
            for invoice_data in payment_data['invoices']:
                if 'invoice_id' not in invoice_data or 'amount' not in invoice_data:
                    raise ValidationError(
                        'Each invoice must have invoice_id and amount')

                invoice = Invoice.objects.get(id=invoice_data['invoice_id'])

                payment_detail = PaymentDetail(
                    payment=payment,
                    invoice=invoice,
                    amount=Decimal(str(invoice_data['amount']))
                )

                # Validar el detalle de pago
                payment_detail.full_clean()
                payment_detail.save()

                total_invoice_amount += payment_detail.amount

            # Validar que el monto total del pago coincida con la suma de los detalles
            if payment.amount != total_invoice_amount:
                raise ValidationError(
                    f'Payment amount ({payment.amount}) does not match sum of invoice amounts ({total_invoice_amount})'
                )

            loggin_event(
                f'Pago creado exitosamente: {payment.payment_number}')

            return JsonResponse({
                'message': 'Payment created successfully',
                'payment_id': payment.id,
                'payment_number': payment.payment_number
            }, status=201)

    def put(self, request, payment_id):
        """Actualizar un pago existente"""
        loggin_event(f'Actualizando pago {payment_id}')

        if not request.body:
            return JsonResponse({'error': 'No data provided'}, status=400)
        payment_data = json.loads(request.body)

        payment = Payment.objects.get(id=payment_id)

        # Verificar que el pago no esté confirmado o aprobado
        if payment.status in ['CONFIRMADO', 'RECHAZADO']:
            return JsonResponse(
                {'error': 'Cannot update a confirmed or rejected payment'},
                status=400
            )

        with transaction.atomic():
            # Actualizar campos del pago
            if 'date' in payment_data:
                payment.date = payment_data['date']
            if 'due_date' in payment_data:
                payment.due_date = payment_data['due_date']
            if 'type_transaction' in payment_data:
                payment.type_transaction = payment_data['type_transaction']
            if 'amount' in payment_data:
                payment.amount = Decimal(str(payment_data['amount']))
            if 'method' in payment_data:
                payment.method = payment_data['method']
            if 'status' in payment_data:
                payment.status = payment_data['status']
            if 'bank' in payment_data:
                payment.bank = payment_data['bank']
            if 'nro_account' in payment_data:
                payment.nro_account = payment_data['nro_account']
            if 'nro_operation' in payment_data:
                payment.nro_operation = payment_data['nro_operation']
            if 'processed_by_id' in payment_data:
                payment.processed_by_id = payment_data['processed_by_id']
            if 'approved_by_id' in payment_data:
                payment.approved_by_id = payment_data['approved_by_id']
            if 'approval_date' in payment_data:
                payment.approval_date = payment_data['approval_date']

            # Si se están actualizando las facturas, eliminar las existentes y crear nuevas
            if 'invoices' in payment_data:
                # Eliminar detalles de pago existentes
                PaymentDetail.objects.filter(payment=payment).delete()

                # Crear nuevos detalles de pago
                total_invoice_amount = Decimal('0')
                for invoice_data in payment_data['invoices']:
                    if 'invoice_id' not in invoice_data or 'amount' not in invoice_data:
                        raise ValidationError(
                            'Each invoice must have invoice_id and amount')

                    invoice = Invoice.objects.get(
                        id=invoice_data['invoice_id'])

                    payment_detail = PaymentDetail(
                        payment=payment,
                        invoice=invoice,
                        amount=Decimal(str(invoice_data['amount']))
                    )

                    payment_detail.full_clean()
                    payment_detail.save()

                    total_invoice_amount += payment_detail.amount

                # Validar que el monto total del pago coincida con la suma de los detalles
                if payment.amount != total_invoice_amount:
                    raise ValidationError(
                        f'Payment amount ({payment.amount}) does not match sum of invoice amounts ({total_invoice_amount})'
                    )

            # Validar el pago antes de guardar
            payment.full_clean()
            payment.save()

            loggin_event(
                f'Pago actualizado exitosamente: {payment.payment_number}')

            return JsonResponse({
                'message': 'Payment updated successfully',
                'payment_id': payment.id,
                'payment_number': payment.payment_number
            }, status=200)

    def get(self, request, payment_id=None):
        """Obtener información de un pago o listar pagos"""
        if payment_id:
            # Obtener un pago específico
            try:
                payment = Payment.objects.get(id=payment_id)
                payment_details = PaymentDetail.objects.filter(payment=payment)

                # Construir respuesta con detalles
                invoices_data = []
                for detail in payment_details:
                    invoices_data.append({
                        'invoice_id': detail.invoice.id,
                        'invoice_number': detail.invoice.num_invoice,
                        'amount': str(detail.amount)
                    })

                payment_data = {
                    'id': payment.id,
                    'payment_number': payment.payment_number,
                    'date': payment.date.isoformat() if payment.date else None,
                    'due_date': payment.due_date.isoformat() if payment.due_date else None,
                    'type_transaction': payment.type_transaction,
                    'amount': str(payment.amount),
                    'method': payment.method,
                    'status': payment.status,
                    'bank': payment.bank,
                    'nro_account': payment.nro_account,
                    'nro_operation': payment.nro_operation,
                    'processed_by_id': payment.processed_by_id,
                    'approved_by_id': payment.approved_by_id,
                    'approval_date': payment.approval_date.isoformat() if payment.approval_date else None,
                    'invoices': invoices_data
                }

                return JsonResponse(payment_data, status=200)

            except Payment.DoesNotExist:
                return JsonResponse({'error': 'Payment not found'}, status=404)
        else:
            # Listar pagos con paginación básica
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 20))

            start = (page - 1) * page_size
            end = start + page_size

            payments = Payment.objects.all()[start:end]
            payments_data = []

            for payment in payments:
                payments_data.append({
                    'id': payment.id,
                    'payment_number': payment.payment_number,
                    'date': payment.date.isoformat() if payment.date else None,
                    'amount': str(payment.amount),
                    'method': payment.method,
                    'status': payment.status,
                    'total_invoices': payment.invoices.count()
                })

            return JsonResponse({
                'payments': payments_data,
                'page': page,
                'page_size': page_size
            }, status=200)
