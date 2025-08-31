import json
from django.http import JsonResponse
from django.views import View
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal

from trade.models import Payment, PaymentDetail, Invoice
from common.AppLoger import loggin_event


class CollectionsCreateUpdateAPI(View):

    def post(self, request):
        """Crear un nuevo cobro"""
        loggin_event('Creando nuevo cobro')

        try:
            # Detectar si es JSON o FormData
            content_type = request.content_type

            if 'application/json' in content_type:
                # Datos JSON
                if not request.body:
                    return JsonResponse({'error': 'No data provided'}, status=400)

                data = json.loads(request.body)
                document_file = None
            else:
                # FormData (para compatibilidad con archivos)
                data = request.POST.dict()
                document_file = request.FILES.get('document')

                # Convertir invoice_collections de JSON string a dict
                if 'invoice_collections' in data:
                    invoice_collections = json.loads(
                        data['invoice_collections'])
                    data['invoices'] = [
                        {'invoice_id': int(inv_id), 'amount': str(amount)}
                        for inv_id, amount in invoice_collections.items()
                    ]

            loggin_event(f'Datos recibidos para cobro: {data}')

            # Validación de campos requeridos
            required_fields = ['date', 'amount', 'method']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Campo requerido: {field}'
                    }, status=400)

            # Validación de facturas
            if 'invoices' not in data or not data['invoices']:
                return JsonResponse({
                    'success': False,
                    'error': 'Debe especificar al menos una factura'
                }, status=400)

            # Validar que el monto total de facturas no exceda el monto del cobro
            total_invoices = sum(
                Decimal(str(inv['amount'])) for inv in data['invoices'])
            collection_amount = Decimal(str(data['amount']))

            if total_invoices > collection_amount:
                return JsonResponse({
                    'success': False,
                    'error': 'El monto total de facturas no puede exceder el monto del cobro'
                }, status=400)

            with transaction.atomic():
                # Crear el cobro (Payment con type_transaction='INGRESO')
                collection = Payment(
                    date=data['date'],
                    due_date=data.get('due_date'),
                    type_transaction='INGRESO',  # Los cobros son ingresos
                    amount=collection_amount,
                    method=data['method'],
                    status=data.get('status', 'CONFIRMADO'),
                    bank=data.get('bank'),
                    nro_account=data.get('nro_account'),
                    nro_operation=data.get('nro_operation'),
                    notes=data.get('notes') or None,
                    processed_by_id=data.get('processed_by'),
                    approved_by_id=data.get('approved_by'),
                    approval_date=data.get('approval_date')
                )

                # Agregar archivo adjunto si existe
                if 'application/json' not in content_type and document_file:
                    collection.document = document_file

                # Validar el cobro
                collection.full_clean()

                # Generar número de cobro si no se proporciona
                if not collection.payment_number:
                    collection.payment_number = (
                        Payment.get_next_collection_number()
                    )

                collection.save()
                loggin_event(f'Cobro creado con ID: {collection.id}')

                # Procesar las facturas asociadas
                total_detail_amount = Decimal('0')

                for invoice_data in data['invoices']:
                    try:
                        invoice = Invoice.objects.get(
                            id=invoice_data['invoice_id'],
                            is_active=True
                        )
                    except Invoice.DoesNotExist:
                        return JsonResponse({
                            'success': False,
                            'error': (
                                'Factura no encontrada: '
                                f'{invoice_data["invoice_id"]}'
                            )
                        }, status=404)

                    detail_amount = Decimal(str(invoice_data['amount']))

                    # Crear el detalle de cobro
                    collection_detail = PaymentDetail(
                        payment=collection,
                        invoice=invoice,
                        amount=detail_amount
                    )

                    collection_detail.full_clean()
                    collection_detail.save()

                    total_detail_amount += detail_amount

                # Verificar total de detalles vs. monto del cobro
                if total_detail_amount != collection_amount:
                    return JsonResponse({
                        'success': False,
                        'error': (
                            'El monto total de facturas '
                            f'({total_detail_amount}) no coincide con '
                            'el monto del cobro '
                            f'({collection_amount})'
                        )
                    }, status=400)

                loggin_event(
                    f'Cobro {collection.payment_number} creado exitosamente'
                )

                # Actualizar el estado de todas las facturas relacionadas
                for invoice_data in data['invoices']:
                    try:
                        invoice = Invoice.objects.get(
                            id=invoice_data['invoice_id']
                        )
                        invoice.update_payment_status()
                    except Invoice.DoesNotExist:
                        pass

                return JsonResponse({
                    'success': True,
                    'message': 'Cobro creado exitosamente',
                    'collection': {
                        'id': collection.id,
                        'payment_number': collection.payment_number,
                        'date': collection.date.isoformat(),
                        'amount': str(collection.amount),
                        'method': collection.method,
                        'status': collection.status
                    }
                })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except ValidationError as e:
            loggin_event(f'Error de validación en cobro: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error de validación: {e}'
            }, status=400)
        except Exception as e:
            loggin_event(f'Error inesperado en cobro: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)

    def put(self, request, collection_id):
        """Actualizar un cobro existente"""
        loggin_event(f'Actualizando cobro ID: {collection_id}')

        try:
            # Buscar el cobro (Payment con type_transaction='INGRESO')
            collection = Payment.objects.get(
                id=collection_id,
                type_transaction='INGRESO',
                is_active=True
            )
        except Payment.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Cobro no encontrado'
            }, status=404)

        try:
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)

            data = json.loads(request.body)
            loggin_event(
                f'Datos para actualizar cobro {collection_id}: {data}'
            )

            # Validar que el total de facturas no exceda el monto del cobro
            if 'invoices' in data and 'amount' in data:
                total_invoices = sum(
                    Decimal(str(inv['amount'])) for inv in data['invoices']
                )
                collection_amount = Decimal(str(data['amount']))

                if total_invoices > collection_amount:
                    return JsonResponse({
                        'success': False,
                        'error': (
                            'El monto total de facturas no puede exceder '
                            'el monto del cobro'
                        )
                    }, status=400)

            with transaction.atomic():
                # Actualizar campos del cobro
                if 'date' in data:
                    collection.date = data['date']
                if 'due_date' in data:
                    collection.due_date = data['due_date']
                if 'amount' in data:
                    collection.amount = Decimal(str(data['amount']))
                if 'method' in data:
                    collection.method = data['method']
                if 'status' in data:
                    collection.status = data['status']
                if 'bank' in data:
                    collection.bank = data['bank']
                if 'nro_account' in data:
                    collection.nro_account = data['nro_account']
                if 'nro_operation' in data:
                    collection.nro_operation = data['nro_operation']
                if 'processed_by' in data:
                    collection.processed_by_id = data['processed_by']
                if 'approved_by' in data:
                    collection.approved_by_id = data['approved_by']
                if 'approval_date' in data:
                    collection.approval_date = data['approval_date']

                # Validar el cobro actualizado
                collection.full_clean()
                collection.save()

                # Si se proporcionan facturas, actualizar los detalles
                if 'invoices' in data:
                    # Eliminar detalles existentes
                    PaymentDetail.objects.filter(payment=collection).delete()

                    # Crear nuevos detalles
                    total_detail_amount = Decimal('0')

                    for invoice_data in data['invoices']:
                        try:
                            invoice = Invoice.objects.get(
                                id=invoice_data['invoice_id'],
                                is_active=True
                            )
                        except Invoice.DoesNotExist:
                            return JsonResponse({
                                'success': False,
                                'error': (
                                    'Factura no encontrada: '
                                    f'{invoice_data["invoice_id"]}'
                                )
                            }, status=404)

                        detail_amount = Decimal(str(invoice_data['amount']))

                        collection_detail = PaymentDetail(
                            payment=collection,
                            invoice=invoice,
                            amount=detail_amount
                        )

                        collection_detail.full_clean()
                        collection_detail.save()

                        total_detail_amount += detail_amount

                    # Verificar que el total de detalles coincida
                    if total_detail_amount != collection.amount:
                        return JsonResponse({
                            'success': False,
                            'error': (
                                'El monto total de facturas '
                                f'({total_detail_amount}) no coincide con '
                                'el monto del cobro '
                                f'({collection.amount})'
                            )
                        }, status=400)

                loggin_event(
                    'Cobro '
                    f'{collection.payment_number} '
                    'actualizado exitosamente'
                )

                return JsonResponse({
                    'success': True,
                    'message': 'Cobro actualizado exitosamente',
                    'collection': {
                        'id': collection.id,
                        'payment_number': collection.payment_number,
                        'date': collection.date.isoformat(),
                        'amount': str(collection.amount),
                        'method': collection.method,
                        'status': collection.status
                    }
                })

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except ValidationError as e:
            loggin_event(f'Error de validación al actualizar cobro: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error de validación: {e}'
            }, status=400)
        except Exception as e:
            loggin_event(f'Error inesperado al actualizar cobro: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)

    def get(self, request, collection_id=None):
        """Obtener uno o varios cobros"""
        try:
            if collection_id:
                # Obtener un cobro específico
                try:
                    collection = Payment.objects.get(
                        id=collection_id,
                        type_transaction='INGRESO',
                        is_active=True
                    )

                    # Obtener detalles de facturas
                    invoices = []
                    for detail in collection.invoices.all():
                        invoices.append({
                            'invoice_id': detail.invoice.id,
                            'invoice_number': detail.invoice.num_invoice,
                            'amount': str(detail.amount)
                        })

                    return JsonResponse({
                        'success': True,
                        'collection': {
                            'id': collection.id,
                            'payment_number': collection.payment_number,
                            'date': collection.date.isoformat(),
                            'due_date': (
                                collection.due_date.isoformat()
                                if collection.due_date else None
                            ),
                            'amount': str(collection.amount),
                            'method': collection.method,
                            'status': collection.status,
                            'bank': collection.bank,
                            'nro_account': collection.nro_account,
                            'nro_operation': collection.nro_operation,
                            'invoices': invoices
                        }
                    })

                except Payment.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'Cobro no encontrado'
                    }, status=404)
            else:
                # Obtener lista de cobros con paginación
                page = int(request.GET.get('page', 1))
                page_size = int(request.GET.get('page_size', 10))
                start = (page - 1) * page_size
                end = start + page_size

                collections = Payment.objects.filter(
                    type_transaction='INGRESO',
                    is_active=True
                ).order_by('-created_at')[start:end]

                total_count = Payment.objects.filter(
                    type_transaction='INGRESO',
                    is_active=True
                ).count()

                collections_list = []
                for collection in collections:
                    total_invoices = collection.total_invoices_amount
                    collections_list.append({
                        'id': collection.id,
                        'payment_number': collection.payment_number,
                        'date': collection.date.isoformat(),
                        'amount': str(collection.amount),
                        'method': collection.method,
                        'status': collection.status,
                        'total_invoices': str(total_invoices),
                        'invoices_count': collection.invoices.count()
                    })

                return JsonResponse({
                    'success': True,
                    'collections': collections_list,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (
                            (total_count + page_size - 1) // page_size
                        )
                    }
                })

        except Exception as e:
            loggin_event(f'Error al obtener cobros: {e}')
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            }, status=500)
