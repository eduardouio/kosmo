from trade.models.Invoice import Invoice
from trade.models.Payment import Payment
from django.db.models import Sum, F
from decimal import Decimal

class SupplierInvoiceBalance:
    @classmethod
    def get_invoice_balance(cls, invoice_id):
        """
        Calcula el saldo pendiente de una factura de venta específica.
        """
        try:
            invoice = Invoice.objects.get(id=invoice_id, is_active=True, type_document='FAC_VENTA')
            
            # Verificar si la factura está anulada
            if invoice.status == 'ANULADO':
                return {
                    'invoice': invoice,
                    'total_amount': invoice.total_invoice,
                    'paid_amount': Decimal('0.00'),
                    'balance': Decimal('0.00'),
                    'status': 'ANULADO'
                }
            
            # Obtener la suma de todos los pagos asociados a esta factura
            payments = Payment.objects.filter(
                invoices=invoice,
                is_active=True
            )
            
            paid_amount = Decimal('0.00')
            for payment in payments:
                # Aquí podríamos tener una lógica más compleja para pagos parciales
                paid_amount += payment.amount
            
            balance = invoice.total_invoice - paid_amount
            
            # Actualizar estado si está completamente pagada
            if balance <= 0 and invoice.status != 'PAGADO':
                invoice.status = 'PAGADO'
                invoice.save()
            elif balance > 0 and invoice.status == 'PAGADO':
                invoice.status = 'PENDIENTE'
                invoice.save()
                
            return {
                'invoice': invoice,
                'total_amount': invoice.total_invoice,
                'paid_amount': paid_amount,
                'balance': balance,
                'status': invoice.status
            }
        except Invoice.DoesNotExist:
            return None
    
    @classmethod
    def get_pending_invoices(cls, partner_id=None):
        """
        Retorna todas las facturas de venta pendientes de cobro, opcionalmente filtradas por cliente.
        """
        query = Invoice.objects.filter(
            is_active=True, 
            status='PENDIENTE',
            type_document='FAC_VENTA'
        )
        
        if partner_id:
            query = query.filter(partner_id=partner_id)
        
        invoices_data = []
        
        for invoice in query:
            balance_data = cls.get_invoice_balance(invoice.id)
            if balance_data and balance_data['balance'] > 0:
                invoices_data.append(balance_data)
                
        return invoices_data
    
    @classmethod
    def apply_collection_to_invoices(cls, payment_id, invoice_amounts):
        """
        Aplica un cobro a múltiples facturas con montos específicos para cada una.
        
        Args:
            payment_id (int): ID del pago/cobro
            invoice_amounts (dict): Diccionario con {invoice_id: monto_a_aplicar}
        """
        try:
            payment = Payment.objects.get(id=payment_id)
            total_applied = Decimal('0.00')
            
            for invoice_id, amount in invoice_amounts.items():
                amount = Decimal(str(amount))
                invoice = Invoice.objects.get(id=invoice_id, type_document='FAC_VENTA')
                payment.invoices.add(invoice)
                total_applied += amount
                
                # Verificar si la factura ya está cobrada completamente
                balance_data = cls.get_invoice_balance(invoice_id)
                if balance_data['balance'] <= 0:
                    invoice.status = 'PAGADO'
                    invoice.save()
            
            return True
        except Exception as e:
            print(f"Error al aplicar cobro: {str(e)}")
            return False
    
    @classmethod
    def get_client_collection_summary(cls, partner_id=None, start_date=None, end_date=None):
        """
        Obtiene un resumen de cobros por cliente en un rango de fechas
        """
        query = Invoice.objects.filter(
            is_active=True,
            type_document='FAC_VENTA'
        )
        
        if partner_id:
            query = query.filter(partner_id=partner_id)
        
        if start_date:
            query = query.filter(date__gte=start_date)
            
        if end_date:
            query = query.filter(date__lte=end_date)
            
        summary = {
            'total_invoiced': Decimal('0.00'),
            'total_collected': Decimal('0.00'),
            'total_pending': Decimal('0.00'),
            'invoices_count': 0,
            'paid_invoices_count': 0,
            'pending_invoices_count': 0,
        }
        
        for invoice in query:
            balance_data = cls.get_invoice_balance(invoice.id)
            if balance_data:
                summary['total_invoiced'] += balance_data['total_amount']
                summary['total_collected'] += balance_data['paid_amount']
                summary['total_pending'] += balance_data['balance']
                summary['invoices_count'] += 1
                
                if balance_data['status'] == 'PAGADO':
                    summary['paid_invoices_count'] += 1
                elif balance_data['status'] == 'PENDIENTE':
                    summary['pending_invoices_count'] += 1
        
        return summary
