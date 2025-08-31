from decimal import Decimal
from django.db.models import Sum, Q, Count
from accounts.models import CustomUserModel
from trade.models import Order, Invoice
from trade.models.Payment import Payment, PaymentDetail
from partners.models import Partner
import json


class SellerData:
    @classmethod
    def get_seller_info(cls, user_id):
        """
        Recopila toda la información de ventas y compras de un vendedor.

        Args:
            user_id: ID del usuario vendedor

        Returns:
            dict: Diccionario con toda la información del vendedor
        """
        try:
            # Obtener el usuario vendedor
            user = CustomUserModel.objects.get(id=user_id)

            # Obtener órdenes del vendedor
            customer_orders = cls._get_customer_orders(user_id)
            supplier_orders = cls._get_supplier_orders(user_id)

            # Obtener estadísticas de ventas
            sales_stats = cls._get_sales_statistics(user_id)

            # Obtener clientes y sus totales
            customers_data = cls._get_customers_summary(user_id)

            # Obtener pendientes
            pending_stats = cls._get_pending_statistics(user_id)

            seller_data = {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'roles': user.roles,
                    'goal_sales': float(user.goal_sales),
                    'goal_stems': float(user.goal_stems)
                },
                'customer_orders': customer_orders,
                'supplier_orders': supplier_orders,
                'stems_sold': sales_stats['stems_sold'],
                'total_sales': sales_stats['total_sales'],
                'sales_by_status': sales_stats['sales_by_status'],
                'customers': customers_data,
                'stems_pending': pending_stats['stems_pending'],
                'pending_buys': pending_stats['pending_buys']
            }

            return seller_data

        except CustomUserModel.DoesNotExist:
            return {'error': f'Usuario con ID {user_id} no encontrado'}
        except Exception as e:
            return {'error': str(e)}

    @classmethod
    def _get_customer_orders(cls, user_id):
        """Obtiene las órdenes de venta del vendedor"""
        orders = Order.objects.filter(
            seller_id=user_id,
            type_document='PED_VENTA',
            is_active=True
        ).values(
            'id',
            'consecutive',
            'date',
            'status',
            'total_price',
            'total_margin',
            'tot_stem_flower'
        )

        return list(orders)

    @classmethod
    def _get_supplier_orders(cls, user_id):
        """Obtiene las órdenes de compra del vendedor"""
        orders = Order.objects.filter(
            seller_id=user_id,
            type_document='PED_COMPRA',
            is_active=True
        ).values(
            'id',
            'consecutive',
            'date',
            'status',
            'total_price',
            'tot_stem_flower'
        )

        return list(orders)

    @classmethod
    def _get_sales_statistics(cls, user_id):
        """Calcula estadísticas de ventas del vendedor"""
        # Obtener facturas de venta del vendedor
        sales_invoices = Invoice.objects.filter(
            order__seller_id=user_id,
            type_document='FAC_VENTA',
            is_active=True
        ).exclude(status='ANULADO')

        # Total de tallos vendidos
        stems_sold = sales_invoices.aggregate(
            total=Sum('tot_stem_flower')
        )['total'] or 0

        # Total de ventas (precio + margen)
        total_sales = Decimal('0.00')
        sales_by_status = {
            'PAGADO': {'count': 0, 'total': Decimal('0.00')},
            'PENDIENTE': {'count': 0, 'total': Decimal('0.00')},
            'ABONADO': {'count': 0, 'total': Decimal('0.00')}
        }

        for invoice in sales_invoices:
            invoice_total = invoice.total_invoice
            total_sales += invoice_total

            # Determinar el estado real basado en pagos
            if invoice.status == 'PAGADO':
                sales_by_status['PAGADO']['count'] += 1
                sales_by_status['PAGADO']['total'] += invoice_total
            else:
                # Verificar si tiene pagos parciales
                paid_amount = invoice.total_paid
                if paid_amount > 0:
                    sales_by_status['ABONADO']['count'] += 1
                    sales_by_status['ABONADO']['total'] += invoice_total
                else:
                    sales_by_status['PENDIENTE']['count'] += 1
                    sales_by_status['PENDIENTE']['total'] += invoice_total

        # Convertir Decimals a float para JSON
        for status in sales_by_status:
            sales_by_status[status]['total'] = float(
                sales_by_status[status]['total'])

        return {
            'stems_sold': stems_sold,
            'total_sales': float(total_sales),
            'sales_by_status': sales_by_status
        }

    @classmethod
    def _get_customers_summary(cls, user_id):
        """Obtiene resumen de clientes del vendedor con sus totales"""
        customers_data = []

        # Obtener clientes únicos a través de las facturas
        customer_ids = Invoice.objects.filter(
            order__seller_id=user_id,
            type_document='FAC_VENTA',
            is_active=True
        ).exclude(
            status='ANULADO'
        ).values_list('partner_id', flat=True).distinct()

        for customer_id in customer_ids:
            customer = Partner.objects.get(id=customer_id)

            # Obtener totales del cliente
            customer_invoices = Invoice.objects.filter(
                order__seller_id=user_id,
                partner_id=customer_id,
                type_document='FAC_VENTA',
                is_active=True
            ).exclude(status='ANULADO')

            customer_stems = customer_invoices.aggregate(
                total=Sum('tot_stem_flower')
            )['total'] or 0

            customer_total = Decimal('0.00')
            for invoice in customer_invoices:
                customer_total += invoice.total_invoice

            customers_data.append({
                'id': customer.id,
                'name': customer.name,
                'short_name': customer.short_name,
                'stems_total': customer_stems,
                'sales_total': float(customer_total),
                'invoices_count': customer_invoices.count()
            })

        # Ordenar por total de ventas descendente
        customers_data.sort(key=lambda x: x['sales_total'], reverse=True)

        return customers_data

    @classmethod
    def _get_pending_statistics(cls, user_id):
        """Obtiene estadísticas de órdenes pendientes"""
        # Estados que indican órdenes pendientes (no facturadas)
        pending_statuses = ['PENDIENTE', 'CONFIRMADO', 'ENVIADO', 'PROCESO']

        # Tallos pendientes de órdenes de venta sin facturar
        pending_sales_orders = Order.objects.filter(
            seller_id=user_id,
            type_document='PED_VENTA',
            is_active=True,
            status__in=pending_statuses
        )

        stems_pending = pending_sales_orders.aggregate(
            total=Sum('tot_stem_flower')
        )['total'] or 0

        # Total de órdenes de compra pendientes
        pending_purchase_orders = Order.objects.filter(
            seller_id=user_id,
            type_document='PED_COMPRA',
            is_active=True,
            status__in=pending_statuses
        )

        pending_buys_total = pending_purchase_orders.aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0.00')

        return {
            'stems_pending': stems_pending,
            'pending_buys': float(pending_buys_total),
            'pending_sales_count': pending_sales_orders.count(),
            'pending_purchase_count': pending_purchase_orders.count()
        }

    @classmethod
    def get_seller_info_json(cls, user_id):
        """
        Retorna la información del vendedor en formato JSON string.

        Args:
            user_id: ID del usuario vendedor

        Returns:
            str: JSON string con la información del vendedor
        """
        seller_data = cls.get_seller_info(user_id)
        return json.dumps(seller_data, ensure_ascii=False, indent=2)

    @classmethod
    def get_all_sellers_summary(cls):
        """
        Obtiene un resumen de todos los vendedores del sistema.

        Returns:
            list: Lista con el resumen de cada vendedor
        """
        sellers = CustomUserModel.get_sellers()
        sellers_summary = []

        for seller in sellers:
            seller_info = cls.get_seller_info(seller.id)
            if 'error' not in seller_info:
                summary = {
                    'user_id': seller.id,
                    'name': f"{seller.first_name} {seller.last_name}",
                    'email': seller.email,
                    'total_sales': seller_info['total_sales'],
                    'stems_sold': seller_info['stems_sold'],
                    'stems_pending': seller_info['stems_pending'],
                    'customers_count': len(seller_info['customers']),
                    'goal_sales': float(seller.goal_sales),
                    'goal_stems': float(seller.goal_stems),
                    'goal_achievement_sales': (
                        (seller_info['total_sales'] /
                         float(seller.goal_sales) * 100)
                        if seller.goal_sales > 0 else 0
                    ),
                    'goal_achievement_stems': (
                        (seller_info['stems_sold'] /
                         float(seller.goal_stems) * 100)
                        if seller.goal_stems > 0 else 0
                    )
                }
                sellers_summary.append(summary)

        return sellers_summary
