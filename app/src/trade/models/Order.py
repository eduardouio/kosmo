from django.db import models
from products.models import StockDetail, Product
from common import BaseModel
from partners.models import Partner

STATUS_CHOICES = (
    ('PENDIENTE', 'PENDIENTE'),
    ('CONFIRMADO', 'CONFIRMADO'),
    ('FACTURADO', 'FACTURADO'),
    ('CANCELADO', 'CANCELADO'),
)

TYPE_DOCUMENT_CHOICES = (
    ('ORD_VENTA', 'ORDEN DE VENTA'),
    ('ORD_COMPRA', 'ORDEN DE COMPRA'),
)

BOX_CHOICES = (
    ('HB', 'HB'),
    ('QB', 'QB'),
    ('FB', 'FB')
)


# la orden del cliente se genera con el pedido y los items
# luego usamos esta orden y generamos ordenes de compra para los proveedores
# varias ordenes de compra pueden ser generadas a partir de una orden de
# cliente la factura se genera a partir de las ordenes de compra
# cuando una orden de cliente no puede ser completada se modifica en la orden
# de compra luego se genera una factura por cada orden de compra
class Order(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    date = models.DateTimeField(
        'Fecha',
        auto_now=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        help_text='C customer S supplier'
    )
    type_document = models.CharField(
        'Tipo de Documento',
        max_length=50,
        choices=TYPE_DOCUMENT_CHOICES
    )
    parent_order = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    num_order = models.CharField(
        'PO Socio',
        max_length=50,
        blank=True,
        null=True,
        help_text='Numero de Orden C para el cliente S para el proveedor autonumerico manual'
    )
    delivery_date = models.DateField(
        'Fecha de entrega',
        blank=True,
        null=True,
        default=None
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
    )
    discount = models.DecimalField(
        'Descuento',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    total_price = models.DecimalField(
        'Precio total',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    qb_total = models.PositiveSmallIntegerField(
        'Total QB',
        default=0
    )
    hb_total = models.PositiveSmallIntegerField(
        'Total QB',
        default=0
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.partner.name}"

    @classmethod
    def get_orders_by_stock_day(cls, stock_day):
        # TODO Validar que retorna
        orders = OrderItems.objects.filter(
            stock_detail__stock_day=stock_day
        ).values_list('order', flat=True).distinct()
        return orders


class OrderItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    stock_detail = models.ForeignKey(
        StockDetail,
        on_delete=models.CASCADE
    )
    line_price = models.DecimalField(
        'Precio Linea',
        max_digits=10,
        decimal_places=2
    )
    qty_stem_flower = models.IntegerField(
        'Unds Tallos',
        default=0,
        help_text='Cantidad de tallos de flor'
    )
    box_model = models.CharField(
        'Tipo de caja',
        max_length=50,
        choices=BOX_CHOICES
    )
    tot_stem_flower = models.IntegerField(
        'Cant Tallos',
        default=0,
        help_text='Cantidad de tallos de flor'
    )
    tot_cost_price_box = models.DecimalField(
        'Precio de costo Caja',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    profit_margin = models.DecimalField(
        'Margen de Ganancia',
        max_digits=5,
        decimal_places=2,
        default=0.06
    )

    @classmethod
    def get_suppliers_by_order(cls, order):
        partners = cls.objects.filter(order=order).values_list(
            'stock_detail__partner', flat=True
        ).distinct()

        if partners:
            return [Partner.get_partner_by_id(x) for x in set(partners)]

        return []

    @classmethod
    def get_supplier_items_by_order(cls, supplier, order):
        line_items = cls.objects.filter(
            order=order,
            stock_detail__partner=supplier
        )
        return line_items

    @classmethod
    def get_order_items_by_order(cls, order):
        return cls.objects.filter(order=order)

    def __str__(self):
        return f"Item {self.id} - {self.stock_detail.product.name}"


class OrderBoxItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    order_item = models.ForeignKey(
        OrderItems,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    length = models.PositiveSmallIntegerField(
        'Largo CM',
    )
    qty_stem_flower = models.IntegerField(
        'Cant Tallos',
        default=0,
        help_text='Cantidad de tallos de flor'
    )
    stem_cost_price = models.DecimalField(
        'Precio de costo Tallo',
        max_digits=10,
        decimal_places=2
    )
    profit_margin = models.DecimalField(
        'Margen de Ganancia',
        max_digits=5,
        decimal_places=2,
        default=0.06
    )
