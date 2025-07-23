from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Sum, Count
from decimal import Decimal
from datetime import date, datetime, timedelta

from partners.models import Partner
from trade.models import Invoice, Payment, PaymentDetail
from common.AppLoger import loggin_event


class PaymentContextData(View):

    def get(self, request):
        """
        Proporciona todos los datos necesarios para el formulario de pagos
        """
        try:
            # Obtener proveedores activos
            suppliers = Partner.objects.filter(
                is_active=True,
                type_partner='PROVEEDOR'
            ).values('id', 'name', 'business_tax_id')

            loggin_event(
                'DEBUG',
                f'PaymentContextData: {len(suppliers)} proveedores encontrados'
            )

            # Obtener facturas de compra pendientes por pagar
            pending_invoices = Invoice.objects.filter(
                type_document='FAC_COMPRA',
                status='PENDIENTE',
                is_active=True
            ).select_related('partner').values(
                'id', 'serie', 'consecutive', 'num_invoice',
                'partner__id', 'partner__name',
                'date', 'due_date', 'total_price'
            )

            loggin_event(
                'DEBUG',
                f'PaymentContextData: {len(pending_invoices)} '
                f'facturas pendientes encontradas'
            )

            # Calcular saldos pendientes por factura
            # (considerando pagos parciales)
            invoices_with_balance = []
            for invoice in pending_invoices:
                try:
                    # Calcular el monto pagado para esta factura
                    # (suma de todos los pagos parciales)
                    paid_amount_result = PaymentDetail.objects.filter(
                        invoice_id=invoice['id'],
                        payment__is_active=True,
                        payment__type_transaction='EGRESO'
                    ).aggregate(total=Sum('amount'))

                    paid_amount = (paid_amount_result['total'] or
                                   Decimal('0.00'))

                    # Convertir a Decimal para cálculos precisos
                    total_amount = Decimal(str(invoice['total_price']))
                    balance = total_amount - paid_amount

                    # Solo incluir facturas con saldo pendiente
                    # Tolerancia para errores de redondeo
                    if balance > Decimal('0.01'):
                        days_overdue = 0

                        # Calcular días vencidos si hay fecha vencimiento
                        if invoice['due_date']:
                            try:
                                if hasattr(invoice['due_date'], 'date'):
                                    due_date = invoice['due_date'].date()
                                else:
                                    due_date = invoice['due_date']

                                if due_date < date.today():
                                    days_overdue = (
                                        date.today() - due_date
                                    ).days
                                else:
                                    days_overdue = -(
                                        (due_date - date.today()).days
                                    )
                            except Exception as date_error:
                                loggin_event(
                                    'WARNING',
                                    f'PaymentContextData: Error calculando '
                                    f'días vencidos para factura '
                                    f'{invoice["id"]}: {str(date_error)}'
                                )
                                days_overdue = 0

                        # Formatear fechas de manera segura
                        formatted_date = ''
                        formatted_due_date = ''

                        try:
                            if invoice['date']:
                                if hasattr(invoice['date'], 'strftime'):
                                    formatted_date = (
                                        invoice['date'].strftime('%Y-%m-%d')
                                    )
                                else:
                                    formatted_date = str(invoice['date'])[:10]
                        except Exception:
                            formatted_date = ''

                        try:
                            if invoice['due_date']:
                                if hasattr(invoice['due_date'], 'strftime'):
                                    formatted_due_date = (
                                        invoice['due_date']
                                        .strftime('%Y-%m-%d')
                                    )
                                else:
                                    formatted_due_date = (
                                        str(invoice['due_date'])[:10]
                                    )
                        except Exception:
                            formatted_due_date = ''

                        invoices_with_balance.append({
                            'id': invoice['id'],
                            'serie': invoice['serie'] or '',
                            'consecutive': invoice['consecutive'] or 0,
                            'num_invoice': invoice['num_invoice'] or '',
                            'partner_id': invoice['partner__id'],
                            'partner_name': (
                                invoice['partner__name'] or 'Sin nombre'
                            ),
                            'date': formatted_date,
                            'due_date': formatted_due_date,
                            'total_amount': float(total_amount),
                            'paid_amount': float(paid_amount),
                            'balance': float(balance),
                            'days_overdue': days_overdue
                        })

                except Exception as invoice_error:
                    loggin_event(
                        'ERROR',
                        f'PaymentContextData: Error procesando factura '
                        f'{invoice.get("id", "unknown")}: {str(invoice_error)}'
                    )
                    continue

            loggin_event(
                'DEBUG',
                f'PaymentContextData: {len(invoices_with_balance)} '
                f'facturas con saldo pendiente'
            )

            # Estadísticas generales de pagos
            current_month = datetime.now().month
            current_year = datetime.now().year

            try:
                # Pagos vencidos
                overdue_payments = Payment.objects.filter(
                    type_transaction='EGRESO',
                    status='PENDIENTE',
                    due_date__lt=date.today(),
                    is_active=True
                ).aggregate(
                    total_amount=Sum('amount'),
                    count=Count('id')
                )

                # Pagos del mes actual
                monthly_payments = Payment.objects.filter(
                    type_transaction='EGRESO',
                    date__month=current_month,
                    date__year=current_year,
                    is_active=True
                ).aggregate(
                    total_amount=Sum('amount'),
                    count=Count('id')
                )

                # Total de facturas pendientes por pagar
                total_pending_invoices = len(invoices_with_balance)
                total_pending_amount = sum(
                    inv['balance'] for inv in invoices_with_balance
                )

                # Facturas próximas a vencer (próximos 30 días)
                next_month_date = date.today() + timedelta(days=30)

                upcoming_invoices = [
                    inv for inv in invoices_with_balance
                    if (inv['due_date'] and
                        datetime.strptime(inv['due_date'], '%Y-%m-%d').date()
                        <= next_month_date)
                ]

            except Exception as stats_error:
                loggin_event(
                    'ERROR',
                    f'PaymentContextData: Error calculando estadísticas: '
                    f'{str(stats_error)}'
                )
                # Valores por defecto si hay error
                overdue_payments = {'total_amount': 0, 'count': 0}
                monthly_payments = {'total_amount': 0, 'count': 0}
                total_pending_invoices = 0
                total_pending_amount = 0
                upcoming_invoices = []

            try:
                # Métodos de pago disponibles
                from trade.models.Payment import METHOD_CHOICES
                payment_methods = [
                    {'value': choice[0], 'label': choice[1]}
                    for choice in METHOD_CHOICES
                ]

                # Bancos más utilizados (últimos 6 meses)
                today = date.today()
                if today.month > 6:
                    six_months_ago = today.replace(month=today.month-6)
                else:
                    six_months_ago = today.replace(
                        month=today.month+6, year=today.year-1
                    )

                popular_banks = Payment.objects.filter(
                    type_transaction='EGRESO',
                    date__gte=six_months_ago,
                    bank__isnull=False,
                    is_active=True
                ).values('bank').annotate(
                    count=Count('id')
                ).order_by('-count')[:10]

            except Exception as config_error:
                loggin_event(
                    'ERROR',
                    f'PaymentContextData: Error obteniendo configuración: '
                    f'{str(config_error)}'
                )
                payment_methods = []
                popular_banks = []

            response_data = {
                'suppliers': list(suppliers),
                'pending_invoices': invoices_with_balance,
                'payment_methods': payment_methods,
                'popular_banks': list(popular_banks),
                'statistics': {
                    'overdue_payments': {
                        'total_amount': float(
                            overdue_payments.get('total_amount', 0) or 0
                        ),
                        'count': overdue_payments.get('count', 0) or 0
                    },
                    'monthly_payments': {
                        'total_amount': float(
                            monthly_payments.get('total_amount', 0) or 0
                        ),
                        'count': monthly_payments.get('count', 0) or 0
                    },
                    'pending_invoices': {
                        'total_amount': float(total_pending_amount),
                        'count': total_pending_invoices
                    },
                    'upcoming_due_invoices': {
                        'count': len(upcoming_invoices),
                        'total_amount': float(
                            sum(inv['balance'] for inv in upcoming_invoices)
                        )
                    }
                },
                'current_date': date.today().strftime('%Y-%m-%d'),
                'success': True
            }

            loggin_event(
                'INFO',
                f'PaymentContextData: Datos obtenidos exitosamente '
                f'para usuario {request.user}. '
                f'Facturas: {len(invoices_with_balance)}, '
                f'Proveedores: {len(suppliers)}'
            )
            return JsonResponse(response_data)

        except Exception as e:
            error_msg = str(e)
            loggin_event(
                'ERROR',
                f'PaymentContextData: Error general - {error_msg}'
            )

            # Intentar obtener más información del error
            import traceback
            traceback_info = traceback.format_exc()
            loggin_event(
                'ERROR',
                f'PaymentContextData: Traceback completo - {traceback_info}'
            )

            return JsonResponse({
                'error': (
                    f'Error al obtener los datos del contexto de pagos: '
                    f'{error_msg}'
                ),
                'success': False,
                'debug_info': (
                    traceback_info if request.user.is_superuser else None
                )
            }, status=500)
