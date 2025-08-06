import json
from django.http import JsonResponse
from django.views import View
from trade.models import Order, OrderItems, OrderBoxItems
from products.models import Product, StockDay
from partners.models import Partner, Contact
from common.SerializerCustomerOrder import SerializerCustomerOrder
from common.SyncOrders import SyncOrders
from common.AppLoger import loggin_event


class CreateOrderAPI(View):

    def post(self, request):
        loggin_event('Creando orden de cliente')
        
        # Manejo de JSON vacío o inválido
        try:
            if not request.body:
                return JsonResponse({'error': 'No data provided'}, status=400)
            order_data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        if not order_data:
            return JsonResponse({'error': 'No data provided'}, status=400)

        # Validar campos requeridos
        required_fields = ['customer', 'stock_day', 'order_detail']
        for field in required_fields:
            if field not in order_data:
                return JsonResponse(
                    {'error': f'Missing required field: {field}'}, 
                    status=400
                )

        # Validar estructura de customer
        if 'id' not in order_data['customer']:
            return JsonResponse(
                {'error': 'Missing customer id'}, 
                status=400
            )

        # Validar estructura de stock_day
        if 'id' not in order_data['stock_day']:
            return JsonResponse(
                {'error': 'Missing stock_day id'}, 
                status=400
            )

        customer = Partner.get_by_id(order_data['customer']['id'])
        if not customer:
            return JsonResponse(
                {'error': 'Customer not found'},
                status=404
            )

        stock_day = StockDay.get_by_id(order_data['stock_day']['id'])
        order = Order.objects.create(
            partner=customer,
            stock_day=stock_day,
            type_document='ORD_VENTA',
            status='PENDIENTE',
            serie='100',
            consecutive=Order.get_next_sale_consecutive()
        )

        for new_order_item in order_data['order_detail']:
            # Manejar stock_detail_id: si es 0 o no existe, usar None
            stock_detail_id = new_order_item.get('stock_detail_id')
            if stock_detail_id == 0:
                stock_detail_id = None
                
            order_item = OrderItems.objects.create(
                order=order,
                id_stock_detail=stock_detail_id,
                box_model=new_order_item['box_model'],
                quantity=new_order_item['quantity'],
            )

            for box_item in new_order_item['box_items']:
                product = Product.get_by_id(box_item['product_id'])

                qty_stem_flower = box_item['qty_stem_flower']
                total_bunches = box_item.get('total_bunches', 0)
                stems_bunch = box_item.get('stems_bunch', 0)

                OrderBoxItems.objects.create(
                    order_item=order_item,
                    product=product,
                    length=box_item['length'],
                    qty_stem_flower=qty_stem_flower,
                    stem_cost_price=box_item['stem_cost_price'],
                    profit_margin=float(box_item['margin']),
                    total_bunches=total_bunches,
                    stems_bunch=stems_bunch,
                )

        Order.rebuild_totals(order)
        loggin_event(f'Orden de cliente {order.id} creada con exito')
        contact = Contact.get_principal_by_partner(order.partner)
        contact_dict = {}
        if contact:
            contact_dict = {
                'name': contact.name,
                'position': contact.position,
                'contact_type': contact.contact_type,
                'phone': contact.phone,
                'email': contact.email,
                'is_principal': contact.is_principal
            }

        order_items = OrderItems.get_by_order(order)
        order_details = [
            SerializerCustomerOrder().get_line(item) for item in order_items
        ]

        loggin_event(f'Orden de cliente {order.id} enviada a sincronizar')
        SyncOrders().sync_suppliers(order,  create=True)

        result = {
            'order': {
                'id': order.id,
                'serie': order.serie,
                'consecutive': order.consecutive,
                'stock_day': order.stock_day.id,
                'date': order.date.isoformat(),
                'status': order.status,
                'type_document': order.type_document,
                'parent_order': order.parent_order,
                'total_price': float(order.total_price),
                'qb_total': order.qb_total,
                'hb_total': order.hb_total,
                'total_stem_flower': order.total_stem_flower,
                'partner': {
                    'id': order.partner.id,
                    'name': order.partner.name,
                    'address': order.partner.address,
                    'phone': order.partner.phone,
                    'email': order.partner.email,
                    'skype': order.partner.skype,
                    'business_tax_id': order.partner.business_tax_id,
                    'contact': contact_dict
                },
            },
            'order_details': order_details,
            'is_selected': False,
            'is_cancelled': False,
            'is_modified': False,
            'is_confirmed': False,
        }
        return JsonResponse(result, status=201, safe=False)
