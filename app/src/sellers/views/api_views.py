from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from partners.models import Partner


@login_required
@require_http_methods(["GET"])
def get_customers_api(request):
    """API para obtener lista de clientes para el selector del modal"""
    try:
        customers = Partner.objects.filter(
            is_customer=True,
            status='active'
        ).values('id', 'name', 'short_name').order_by('name')
        
        customers_list = list(customers)
        
        return JsonResponse({
            'success': True,
            'customers': customers_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def create_order_api(request):
    """API para crear una nueva orden desde el modal"""
    import json
    from django.utils import timezone
    from trade.models import Order
    from decimal import Decimal
    
    try:
        data = json.loads(request.body)
        
        # Validar datos requeridos
        customer_id = data.get('customer_id')
        if not customer_id:
            return JsonResponse({'success': False, 'error': 'Cliente requerido'}, status=400)
            
        customer = Partner.objects.get(id=customer_id, is_customer=True)
        
        # Crear la orden
        order = Order.objects.create(
            customer=customer,
            seller=request.user,
            po_customer=data.get('po_customer', ''),
            delivery_date=data.get('delivery_date'),
            discount_percent=Decimal(data.get('discount_percent', 0)),
            status='PENDING',
            created_date=timezone.now()
        )
        
        # Si hay items preseleccionados, agregarlos
        preselected = data.get('preselected')
        if preselected:
            # Aquí se agregarían los items preseleccionados
            # según el tipo (stock completo o variedad específica)
            pass
        
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'message': f'Orden #{order.id} creada exitosamente'
        })
        
    except Partner.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Cliente no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
