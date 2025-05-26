from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Sum, Count, Case, When, DecimalField
from django.utils.dateparse import parse_date
from datetime import date, datetime, timedelta
from trade.models.Payment import Payment
from trade.models.Invoice import Invoice
from partners.models.Partner import Partner


class CollectionsListAPI(APIView):
    """
    API para listado de cobros recibidos (ingresos) con estadísticas
    """
    
    def get(self, request):
        try:
            # Filtros de consulta
            status_filter = request.GET.get('status', None)
            partner_id = request.GET.get('partner_id', None)
            date_from = request.GET.get('date_from', None)
            date_to = request.GET.get('date_to', None)
            method = request.GET.get('method', None)
            overdue_only = request.GET.get('overdue_only', False)
            
            # Query base - solo ingresos (cobros recibidos)
            queryset = Payment.objects.filter(
                type_transaction='INGRESO',
                is_active=True
            ).select_related().prefetch_related('invoices', 'invoices__partner')
            
            # Aplicar filtros
            if status_filter:
                queryset = queryset.filter(status=status_filter)
            
            if partner_id:
                queryset = queryset.filter(invoices__partner_id=partner_id)
            
            if date_from:
                date_from_parsed = parse_date(date_from)
                if date_from_parsed:
                    queryset = queryset.filter(date__gte=date_from_parsed)
            
            if date_to:
                date_to_parsed = parse_date(date_to)
                if date_to_parsed:
                    queryset = queryset.filter(date__lte=date_to_parsed)
            
            if method:
                queryset = queryset.filter(method=method)
            
            if overdue_only and overdue_only.lower() == 'true':
                queryset = queryset.filter(
                    status='PENDIENTE',
                    due_date__lt=date.today()
                )
            
            # Ordenar por fecha descendente
            queryset = queryset.order_by('-date', '-id')
            
            # Serializar datos
            collections_data = []
            for payment in queryset:
                invoices_info = []
                total_invoices = 0
                partners_info = []
                
                for invoice in payment.invoices.all():
                    invoices_info.append({
                        'id': invoice.id,
                        'num_invoice': invoice.num_invoice,
                        'total': float(invoice.total_invoice),
                        'partner': {
                            'id': invoice.partner.id,
                            'name': invoice.partner.name,
                            'short_name': invoice.partner.short_name
                        }
                    })
                    total_invoices += invoice.total_invoice
                    
                    # Agregar partner si no está ya en la lista
                    partner_exists = any(p['id'] == invoice.partner.id for p in partners_info)
                    if not partner_exists:
                        partners_info.append({
                            'id': invoice.partner.id,
                            'name': invoice.partner.name,
                            'short_name': invoice.partner.short_name
                        })
                
                collection_data = {
                    'id': payment.id,
                    'payment_number': payment.payment_number,
                    'date': payment.date.isoformat(),
                    'due_date': payment.due_date.isoformat() if payment.due_date else None,
                    'amount': float(payment.amount),
                    'method': payment.method,
                    'method_display': payment.get_method_display(),
                    'status': payment.status,
                    'status_display': payment.get_status_display(),
                    'bank': payment.bank,
                    'nro_operation': payment.nro_operation,
                    'nro_account': payment.nro_account,
                    'is_overdue': payment.is_overdue,
                    'invoices': invoices_info,
                    'partners': partners_info,
                    'total_invoices_amount': float(total_invoices),
                    'processed_by': {
                        'id': payment.processed_by.id,
                        'username': payment.processed_by.username,
                        'full_name': f"{payment.processed_by.first_name} {payment.processed_by.last_name}"
                    } if payment.processed_by else None,
                    'approved_by': {
                        'id': payment.approved_by.id,
                        'username': payment.approved_by.username,
                        'full_name': f"{payment.approved_by.first_name} {payment.approved_by.last_name}"
                    } if payment.approved_by else None,
                    'approval_date': payment.approval_date.isoformat() if payment.approval_date else None
                }
                collections_data.append(collection_data)
            
            # Calcular estadísticas
            stats = self.calculate_collection_statistics()
            
            return Response({
                'success': True,
                'data': collections_data,
                'statistics': stats,
                'total_records': len(collections_data)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def calculate_collection_statistics(self):
        """
        Calcula estadísticas de cobros recibidos
        """
        today = date.today()
        
        # Cobros totales por estado
        collection_stats = Payment.objects.filter(
            type_transaction='INGRESO',
            is_active=True
        ).aggregate(
            total_pending=Sum(
                Case(
                    When(status='PENDIENTE', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_confirmed=Sum(
                Case(
                    When(status='CONFIRMADO', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_rejected=Sum(
                Case(
                    When(status='RECHAZADO', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            total_cancelled=Sum(
                Case(
                    When(status='ANULADO', then='amount'),
                    default=0,
                    output_field=DecimalField()
                )
            ),
            count_pending=Count(
                Case(
                    When(status='PENDIENTE', then=1),
                    output_field=DecimalField()
                )
            ),
            count_confirmed=Count(
                Case(
                    When(status='CONFIRMADO', then=1),
                    output_field=DecimalField()
                )
            )
        )
        
        # Cobros vencidos
        overdue_collections = Payment.objects.filter(
            type_transaction='INGRESO',
            status='PENDIENTE',
            due_date__lt=today,
            is_active=True
        ).aggregate(
            total_overdue=Sum('amount'),
            count_overdue=Count('id')
        )
        
        # Facturas cobradas (con cobros confirmados)
        collected_invoices = Invoice.objects.filter(
            payment__type_transaction='INGRESO',
            payment__status='CONFIRMADO',
            payment__is_active=True,
            is_active=True
        ).distinct().aggregate(
            total_collected_invoices=Sum('total_price'),
            count_collected_invoices=Count('id')
        )
        
        return {
            'collections': {
                'total_pending_amount': float(collection_stats['total_pending'] or 0),
                'total_confirmed_amount': float(collection_stats['total_confirmed'] or 0),
                'total_rejected_amount': float(collection_stats['total_rejected'] or 0),
                'total_cancelled_amount': float(collection_stats['total_cancelled'] or 0),
                'count_pending': int(collection_stats['count_pending'] or 0),
                'count_confirmed': int(collection_stats['count_confirmed'] or 0),
                'total_overdue_amount': float(overdue_collections['total_overdue'] or 0),
                'count_overdue': int(overdue_collections['count_overdue'] or 0)
            },
            'invoices': {
                'total_collected_amount': float(collected_invoices['total_collected_invoices'] or 0),
                'count_collected': int(collected_invoices['count_collected_invoices'] or 0)
            }
        }
