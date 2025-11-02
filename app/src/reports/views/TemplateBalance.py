from django.views.generic import TemplateView
from django.db.models import Sum
from datetime import date, datetime, timedelta

from trade.models import Invoice
from trade.models.Payment import PaymentDetail
from partners.models import Partner
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event


class TemplateBalance(TemplateView):
    template_name = 'reports/status_account.html'

    def _parse_date(self, value, default):
        """Parsea una fecha desde string o retorna valor por defecto"""
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except Exception:
            return default

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener parámetros de la URL
        partner_id = kwargs.get('partner_id')
        today = date.today()
        
        # Configurar rango de fechas por defecto (mes actual)
        first_day = today.replace(day=1)
        next_month = (
            first_day.replace(day=28) + timedelta(days=4)
        ).replace(day=1)
        last_day = next_month - timedelta(days=1)
        
        # Obtener fechas de los parámetros GET si existen
        start_param = self.request.GET.get('start_date')
        end_param = self.request.GET.get('end_date')
        
        start_date = self._parse_date(start_param, first_day)
        end_date = self._parse_date(end_param, last_day)
        
        # Datos básicos del contexto
        context.update({
            'start_date': start_date,
            'end_date': end_date,
            'today': today,
        })
        
        # Si no hay partner_id, mostrar mensaje
        if not partner_id:
            context['partner'] = None
            return context
        
        try:
            partner = Partner.objects.get(id=partner_id)
            context['partner'] = partner
        except Partner.DoesNotExist:
            loggin_event(
                f"Partner con ID {partner_id} no encontrado", error=True
            )
            context['partner'] = None
            return context
        
        # Facturas dentro del rango
        invoices_in_range = Invoice.objects.filter(
            partner=partner,
            is_active=True,
            status__in=['PENDIENTE', 'PAGADO'],
            date__date__gte=start_date,
            date__date__lte=end_date,
        )
        
        # Facturas pendientes (todas, incluso fuera del rango)
        pending_invoices = Invoice.objects.filter(
            partner=partner,
            is_active=True,
            status='PENDIENTE'
        )
        
        # Unir ambos conjuntos de facturas
        invoice_ids = (
            set(invoices_in_range.values_list('id', flat=True)) |
            set(pending_invoices.values_list('id', flat=True))
        )
        
        invoices = (
            Invoice.objects.filter(id__in=invoice_ids)
            .select_related('partner')
            .order_by('date')
        )
        
        # Pagos del rango vinculados a facturas incluidas
        payment_details = PaymentDetail.objects.filter(
            invoice_id__in=invoice_ids,
            payment__date__gte=start_date,
            payment__date__lte=end_date,
            is_active=True,
            payment__is_active=True,
        ).select_related('payment', 'invoice').order_by(
            'payment__date', 'id'
        )
        
        # Indexar pagos por factura
        payments_by_invoice = {}
        for pd in payment_details:
            payments_by_invoice.setdefault(pd.invoice_id, []).append(pd)
        
        # Procesar entradas para el estado de cuenta
        entries = []
        total_invoices_amount = 0
        total_payments_amount = 0
        total_pending_balance = 0
        net_balance = 0
        total_overdue_amount = 0  # Valor vencido
        invoice_count = 0  # Cantidad de comprobantes
        
        def _to_date(val):
            """Convierte valor a date"""
            if not val:
                return None
            if isinstance(val, datetime):
                return val.date()
            return val
        
        for inv in invoices:
            invoice_count += 1  # Contar comprobante
            
            # Total de pagos aplicados (activos) a la factura
            all_payments_sum = (
                PaymentDetail.objects.filter(
                    invoice=inv,
                    is_active=True,
                    payment__is_active=True,
                ).aggregate(s=Sum('amount'))['s'] or 0
            )
            
            # Calcular balance (permitir negativo para saldo a favor)
            # Usar total_invoice que incluye el margen para facturas de venta
            balance = (inv.total_invoice or 0) - all_payments_sum
            
            # Calcular días de crédito restantes
            inv_date_only = _to_date(inv.date)
            days_passed = (today - inv_date_only).days if inv_date_only else 0
            credit_term = getattr(inv.partner, 'credit_term', 0) or 0
            credit_days = credit_term - days_passed
            
            # Determinar referencia del estado
            if inv.status == 'ANULADO':
                reference = 'FACTURA ANULADA'
            elif balance == 0:
                reference = 'FACTURA PAGADA'
            elif credit_days < 0:
                reference = 'FACTURA VENCIDA'
                # Sumar al total de valores vencidos (solo si tiene balance pendiente)
                if balance > 0:
                    total_overdue_amount += float(balance)
            else:
                reference = 'FACTURA'
            
            # Pagos en el rango para esta factura
            invoice_payments_in_range = payments_by_invoice.get(inv.id, [])
            payments_amount_in_range = sum(
                p.amount for p in invoice_payments_in_range
            )
            
            # Agregar factura a las entradas
            entries.append({
                'type': 'INVOICE',
                'date': inv_date_only,
                'document': inv.num_invoice or f'INV-{inv.id}',
                'credit_days': credit_days,
                # Usar total_invoice para incluir margen en facturas de venta
                'invoice_amount': inv.total_invoice,
                'payment_amount': (
                    payments_amount_in_range
                    if payments_amount_in_range else None
                ),
                'balance': balance,
                'reference': reference,
                'invoice': inv,
            })
            
            # Actualizar totales usando total_invoice que incluye margen
            total_invoices_amount += float(inv.total_invoice or 0)
            total_payments_amount += float(payments_amount_in_range)
            if inv.status == 'PENDIENTE' and balance > 0:
                total_pending_balance += float(balance)
            net_balance += float(balance)
            
        # Ordenar entradas: fecha, luego tipo (factura antes que pago)
        entries.sort(
            key=lambda e: (
                e['date'] or date.min,
                0 if e['type'] == 'INVOICE' else 1,
            )
        )
        
        # Agregar datos del usuario que genera el reporte
        try:
            # Usar el usuario actual de la request si está disponible
            user_id = (
                getattr(self.request.user, 'id', 1)
                if hasattr(self.request, 'user') else 1
            )
            user_owner = CustomUserModel.get_by_id(user_id)
            context['user_owner'] = user_owner
        except Exception as e:
            loggin_event(
                f"Error al obtener usuario para el reporte: {str(e)}",
                error=True
            )
            context['user_owner'] = None
        
        # Actualizar contexto con todos los datos calculados
        context.update({
            'entries': entries,
            'total_invoices_amount': total_invoices_amount,
            'total_payments_amount': total_payments_amount,
            'total_pending_balance': total_pending_balance,
            'net_balance': net_balance,
            'invoice_count': invoice_count,
            'total_overdue_amount': total_overdue_amount,
        })
        
        return context
