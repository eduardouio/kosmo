from django.db import models
from common import BaseModel
from .Order import Order, OrderItems
from products.models import Product
from common.AppLoger import loggin_event


STATUS_CHOICES = (
    ('PENDIENTE', 'PENDIENTE'),
    ('PAGADO', 'PAGADO'),
    ('ANULADO', 'ANULADO'),
)

TYPE_DOCUMENT_CHOICES = (
    ('FAC_VENTA', 'FACTURA VENTA'),
    ('FAC_COMPRA', 'FACTURA COMPRA'),
)

BOX_CHOICES = (
    ('HB', 'HB'),
    ('QB', 'QB'),
    ('FB', 'FB')
)


class Invoice(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.CASCADE
    )
    num_invoice = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        default='',
    )
    type_document = models.CharField(
        'Tipo de Documento',
        max_length=50,
        choices=TYPE_DOCUMENT_CHOICES,
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
        decimal_places=2,
        default=0
    )
    total_margin = models.DecimalField(
        'Margen total',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    comision_seler = models.DecimalField(
        'Comisión Vendedor',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    qb_total = models.PositiveSmallIntegerField(
        'Total QB',
        blank=True,
        null=True,
        default=0
    )
    hb_total = models.PositiveSmallIntegerField(
        'Total HB',
        blank=True,
        null=True,
        default=0
    )
    tot_stem_flower = models.IntegerField(
        'Cantidad Total de Tallos',
        blank=True,
        null=True,
        default=0,
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
            ('PENDIENTE', 'PENDIENTE'),
            ('PAGADO', 'PAGADO'),
            ('ANULADO', 'ANULADO')
        ),
        default='PENDIENTE'
    )

    @classmethod
    def get_next_invoice_number(cls):
        last_invoice = cls.objects.filter(type_document='FAC_VENTA').last()

        if last_invoice:
            return last_invoice.num_invoice + 1
        return 1

    @classmethod
    def get_by_type(cls, type_document):
        return cls.objects.filter(type_document=type_document)

    @classmethod
    def disable_invoice_items(cls, invoice):
        loggin_event(f"Desactivando items de factura {invoice.id}")
        invoice_items = InvoiceItems.get_invoice_items(invoice)
        for invoice_item in invoice_items:
            invoice_item.is_active = False
            invoice_item.save()
            InvoiceBoxItems.disable_by_invoice_items(invoice_item)

    @classmethod
    def rebuild_totals(cls, invoice):
        loggin_event(f"Reconstruyendo totales de factura {invoice.id}")
        total_price = 0
        total_margin = 0
        total_invoice = 0
        qb_total = 0
        hb_total = 0
        total_stem_flower = 0

        for invoice_item in InvoiceItems.get_invoice_items(invoice):
            InvoiceItems.rebuild_invoice_item(invoice_item)

        for invoice_item in InvoiceItems.get_invoice_items(invoice):
            total_price += invoice_item.line_price
            total_margin += invoice_item.line_margin
            total_invoice += invoice_item.line_total
            total_stem_flower += invoice_item.tot_stem_flower

            if invoice_item.box_model == 'QB':
                qb_total += invoice_item.quantity
            elif invoice_item.box_model == 'HB':
                hb_total += invoice_item.quantity

        invoice.qb_total = qb_total
        invoice.hb_total = hb_total
        invoice.total_margin = total_margin
        invoice.tot_stem_flower = total_stem_flower

        if invoice.type_document == 'FAC_VENTA':
            invoice.total_price = total_invoice
        else:
            invoice.total_price = total_price

        invoice.save()

    def __str__(self):
        return f"Factura {self.id} - Pedido {self.order.id}"


class InvoiceItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )
    id_order_item = models.PositiveSmallIntegerField(
        'ID Item Orden',
        blank=True,
        null=True,
        default=0
    )
    box_model = models.CharField(
        'Tipo de caja',
        max_length=50,
        choices=BOX_CHOICES
    )
    quantity = models.PositiveSmallIntegerField(
        'Cant Cajas',
        default=0
    )
    tot_stem_flower = models.IntegerField(
        'Cantidad Tallos',
        default=0
    )
    line_price = models.DecimalField(
        'Precio Linea',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    line_margin = models.DecimalField(
        'Margen Linea',
        max_digits=5,
        decimal_places=2,
        default=0.06
    )
    line_total = models.DecimalField(
        'Precio Total',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    @classmethod
    def get_invoice_items(cls, invoice):
        return cls.objects.filter(invoice=invoice)

    @classmethod
    def rebuild_invoice_item(cls, invoice_item):
        loggin_event(f"Reconstruyendo item de factura {invoice_item.id}")
        box_items = InvoiceBoxItems.get_box_items(invoice_item)
        total_stem_flower = sum(box.qty_stem_flower for box in box_items)
        total_cost_price = sum(
            (box.stem_cost_price * box.qty_stem_flower) for box in box_items
        )
        total_margin = sum(
            (box.profit_margin * box.qty_stem_flower) for box in box_items
        )

        invoice_item.tot_stem_flower = (
            total_stem_flower * invoice_item.quantity
        )
        invoice_item.line_price = total_cost_price * invoice_item.quantity
        invoice_item.line_margin = total_margin * invoice_item.quantity
        invoice_item.line_total = (total_cost_price + total_margin) * invoice_item.quantity
        invoice_item.save()

    def __str__(self):
        return f"Item {self.id} - {self.invoice}"


class InvoiceBoxItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    invoice_item = models.ForeignKey(
        InvoiceItems,
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

    @classmethod
    def disable_by_invoice_items(cls, invoice_item):
        box_items = cls.get_box_items(invoice_item)
        for box_item in box_items:
            box_item.is_active = False
            box_item.save()

    @classmethod
    def get_box_items(cls, invoice_item):
        return cls.objects.filter(
            invoice_item=invoice_item,
            is_active=True
        )
