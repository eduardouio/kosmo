from django.db import models
from products.models import StockDetail
from common import BaseModel
from partners.models import Partner

STATUS_CHOICES = (
    ('pending', 'Pendiente'),
    ('delivered', 'Entregado'),
    ('cancelled', 'Cancelado'),
    ('invoiced', 'Facturado'),
)

TYPE_DOCUMENT_CHOICES = (
    ('client_order', 'Orden de Cliente'),
    ('supplier_order', 'Orden de Proveedor'),
)

BOX_CHOICES = (
    ('hb', 'HB'),
    ('qb', 'QB'),
    ('fb', 'FB')
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
    purchase_order = models.ForeignKey(
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
        null=True
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
    )
    discount = models.DecimalField(
        'Descuento',
        max_digits=10,
        decimal_places=2
    )
    total_price = models.DecimalField(
        'Precio total',
        max_digits=10,
        decimal_places=2
    )
    qb_total = models.PositiveSmallIntegerField(
        'Total QB',
    )
    hb_total = models.PositiveSmallIntegerField(
        'Total QB',
    )

    def __str__(self):
        return f"Pedido {self.id} - {self.customer.name}"


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
    quantity = models.IntegerField(
        'Cantidad',
        default=0
    )
    line_price = models.DecimalField(
        'Precio',
        max_digits=10,
        decimal_places=2
    )
    stem_flower = models.IntegerField(
        'Tallo Flor',
        default=0,
        help_text='Cantidad de tallos de flor'
    )
    box = models.CharField(
        'Tipo de caja',
        max_length=50,
        choices=BOX_CHOICES
    )

    def __str__(self):
        return f"Item {self.id} - {self.product.name}"
