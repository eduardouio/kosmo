from products.models import StockDay, StockDetail, BoxItems
from trade.models.Order import Order, OrderItems, OrderBoxItems
from common.SerializerStock import SerializerStock
from common.AppLoger import loggin_event


class StockDispoQuantity:
    """
    Clase que calcula las cantidades disponibles de stock
    restando las cantidades ya asignadas a órdenes activas no canceladas
    """
    
    def __init__(self, stock_day_id):
        self.stock_day_id = stock_day_id
        self.stock_day = StockDay.get_by_id(stock_day_id)
        
    def get_available_stock(self):
        """
        Obtiene el stock disponible restando las cantidades ya asignadas
        a órdenes activas no canceladas
        """
        if not self.stock_day:
            return {
                'error': 'No hay disponibilidad para esta fecha',
                'status': 404
            }
            
        stock_details = StockDetail.get_by_stock_day(self.stock_day)
        if not stock_details:
            return {
                'error': 'No hay detalles para esta disponibilidad, '
                         'debe importar primero',
                'status': 404
            }
            
        result_dict = []
        
        for stock in stock_details:
            # Obtener la información básica del stock usando el serializer
            stock_data = SerializerStock().get_line(stock)
            
            # Calcular las cantidades ya asignadas a órdenes
            assigned_quantities = self._get_assigned_quantities(stock.id)
            
            # Restar las cantidades asignadas de las cantidades disponibles
            total_assigned = assigned_quantities['total_boxes']
            available_quantity = max(0, stock.quantity - total_assigned)
            stock_data['quantity'] = available_quantity
            
            # Ajustar también las cantidades de los box_items si es necesario
            for box_item in stock_data['box_items']:
                box_id = box_item['id']
                box_assigned = assigned_quantities['box_items'].get(box_id, 0)
                original_qty = box_item['qty_stem_flower']
                available_qty = max(0, original_qty - box_assigned)
                box_item['qty_stem_flower'] = available_qty
                
            # Marcar si el stock está en uso en órdenes
            stock_data['is_in_order'] = assigned_quantities['total_boxes'] > 0
            
            result_dict.append(stock_data)
            
        return {
            'stock': result_dict,
            'stockDay': {
                'id': self.stock_day.id,
                'date': self.stock_day.date,
                'is_active': self.stock_day.is_active,
            },
            'orders': self._get_related_orders(),
            'status': 200
        }
    
    def _get_assigned_quantities(self, stock_detail_id):
        """
        Calcula las cantidades ya asignadas a órdenes activas no canceladas
        para un stock_detail específico
        """
        loggin_event(
            f"Calculando cantidades asignadas para stock_detail "
            f"{stock_detail_id}"
        )
        
        # Obtener todas las OrderItems que referencian este stock_detail
        # Solo considerar órdenes activas y no canceladas
        allowed_statuses = [
            'PENDIENTE', 'CONFIRMADO', 'MODIFICADO', 'FACTURADO', 'PROMESA'
        ]
        order_items = OrderItems.objects.filter(
            id_stock_detail=stock_detail_id,
            is_active=True,
            order__is_active=True,
            order__status__in=allowed_statuses
        )
        
        total_boxes = 0
        box_items_assigned = {}
        
        for order_item in order_items:
            # Sumar la cantidad de cajas asignadas
            total_boxes += order_item.quantity
            
            # Calcular cantidades por box_item
            order_box_items = OrderBoxItems.get_box_items(order_item)
            for order_box_item in order_box_items:
                # Necesitamos encontrar el BoxItem original correspondiente
                # para obtener su ID real
                stock_detail_id = order_item.id_stock_detail
                stock_detail = StockDetail.get_by_id(stock_detail_id)
                if stock_detail:
                    stock_box_items = BoxItems.get_box_items(stock_detail)
                    for stock_box_item in stock_box_items:
                        # Comparamos por product_id y length para encontrar
                        # el BoxItem correspondiente
                        same_product = (
                            stock_box_item.product_id ==
                            order_box_item.product_id
                        )
                        same_length = (
                            stock_box_item.length == order_box_item.length
                        )
                        if same_product and same_length:
                            box_id = stock_box_item.id
                            if box_id not in box_items_assigned:
                                box_items_assigned[box_id] = 0
                            stem_qty = order_box_item.qty_stem_flower
                            order_qty = order_item.quantity
                            quantity_assigned = stem_qty * order_qty
                            box_items_assigned[box_id] += quantity_assigned
                            break
        
        return {
            'total_boxes': total_boxes,
            'box_items': box_items_assigned
        }
    
    def _get_related_orders(self):
        """
        Obtiene las órdenes relacionadas con este stock_day
        """
        orders = Order.get_sales_by_stock_day(self.stock_day)
        return [order.id for order in orders if order.status != 'CANCELADO']
