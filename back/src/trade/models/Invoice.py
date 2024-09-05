from django.db import models
from common import BaseModel
from .Order import Order, OrderItems
TYPE_DOCUMENT_CHOICES = (
    ('client_invoice', 'Factura de Cliente'),
    ('supplier_invoice', 'Factura de Proveedor'),
)

# las compras siempre son locales, las ventas son exportación o local
TYPE_INVOICE_CHOICES = (
    ('export', 'Exportación'),
    ('local', 'Nacional'),
)


BOX_CHOICES = (
    ('hb', 'HB'),
    ('qb', 'QB'),
    ('fb', 'FB')
)


class Invoice(BaseModel):
    id_invoice = models.AutoField(
        primary_key=True
    )
    purcharse_order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.CASCADE
    )
    num_invoice = models.CharField(
        'Numero de Factura',
        max_length=50,
        help_text='Numero de Factura C para el cliente S para el proveedor'
    )
    type_document = models.CharField(
        'Tipo de Documento',
        max_length=50,
        choices=TYPE_DOCUMENT_CHOICES,
    )
    type_invoice = models.CharField(
        'Tipo de Factura',
        max_length=50,
        choices=TYPE_INVOICE_CHOICES,
    )
    date = models.DateTimeField(
        'Fecha',
        auto_now=True
    )
    due_date = models.DateField(
        'Fecha de vencimiento',
        blank=True,
        null=True
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
        'Total HB',
    )
    awb = models.CharField(
        'MAWB',
        max_length=50,
        blank=True,
        null=True
    )
    dae_export = models.CharField(
        'DAE Exportación',
        max_length=50,
        blank=True,
        null=True
    )
    hawb = models.CharField(
        'HAWB',
        max_length=50,
        blank=True,
        null=True
    )
    cargo_agency = models.CharField(
        'Agencia de Carga',
        max_length=50,
        blank=True,
        null=True
    )
    delivery_date = models.DateField(
        'Fecha de entrega',
        blank=True,
        null=True
    )
    weight = models.DecimalField(
        'Peso KG',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    status = models.CharField(
        'Estado',
        max_length=50,
        choices=(
            ('pending', 'Pendiente'),
            ('paid', 'Pagado'),
            ('void', 'Anulado')
        ),
        default='pending'
    )

    def __str__(self):
        return f"Factura {self.id} - Pedido {self.order.id}"


class InvoiceItems(BaseModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )
    order_item = models.ForeignKey(
        OrderItems,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        'Cantidad Tallos',
        default=0
    )
    line_price = models.DecimalField(
        'Precio',
        max_digits=10,
        decimal_places=2
    )
    line_discount = models.DecimalField(
        'Descuento',
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
        return f"Item {self.id} - {self.invoice.order.customer.name}"