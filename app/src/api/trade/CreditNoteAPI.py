from django.http import JsonResponse
from django.views import View
from django.db.models import Sum
from trade.models.Invoice import Invoice
from trade.models.CreditNote import CreditNote


class CreditNoteInvoicesAPI(View):
    """API para obtener facturas disponibles para nota de crédito"""
    
    def get(self, request, *args, **kwargs):
        partner_id = request.GET.get("partner_id")
        
        if not partner_id:
            return JsonResponse({
                "success": False, 
                "error": "Se requiere partner_id"
            }, status=400)
        
        try:
            invoices = Invoice.objects.filter(
                partner_id=partner_id,
                is_active=True
            ).exclude(
                status="ANULADO"
            ).order_by('-date')
            
            invoice_list = []
            for inv in invoices:
                total_price = float(inv.total_price or 0)
                
                # Calcular total pagado (si existe el campo o método)
                total_paid = 0
                if hasattr(inv, 'total_paid'):
                    total_paid = float(inv.total_paid or 0)
                elif hasattr(inv, 'get_total_paid'):
                    total_paid = float(inv.get_total_paid() or 0)
                
                # Calcular notas de crédito aplicadas a esta factura
                credit_notes_applied = CreditNote.objects.filter(
                    invoice=inv,
                    is_active=True,
                    status="APLICADO"
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                # Saldo pendiente = Total - Pagado - Notas de crédito
                pending = total_price - total_paid - float(credit_notes_applied)
                
                if pending > 0:  # Solo facturas con saldo pendiente
                    invoice_list.append({
                        "id": inv.id,
                        "display_number": f"{inv.serie}-{inv.consecutive:06d}",
                        "date": inv.date.strftime("%Y-%m-%d") if inv.date else "",
                        "total_price": total_price,
                        "pending_balance": pending,
                        "type_document": inv.type_document,
                    })
            
            return JsonResponse({
                "success": True,
                "invoices": invoice_list
            })
            
        except Exception as e:
            return JsonResponse({
                "success": False,
                "error": str(e)
            }, status=500)
