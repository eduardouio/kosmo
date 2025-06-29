from django.db import models
from common import BaseModel
from trade.models import Order
from products.models import Product
from common.AppLoger import loggin_event
from datetime import datetime


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
    ('EB', 'EB'),
    ('HB', 'HB'),
    ('QB', 'QB'),
    ('FB', 'FB')
)

SERIES = (
    ('300', '300'),
    ('000', '000'),
)


class Invoice(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    serie = models.CharField(
        'Serie',
        max_length=5,
        blank=True, 
        null=True,
        default=None,
        choices=SERIES
    )
    consecutive = models.PositiveSmallIntegerField(
        'Consecutivo',
        blank=True,
        null=True,
        default=None
    )
    marking = models.CharField(
        'Marcación',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.RESTRICT
    )
    partner = models.ForeignKey(
        'partners.Partner',
        on_delete=models.RESTRICT
    )
    num_invoice = models.CharField(
        max_length=50,
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
    due_date = models.DateTimeField(
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
    eb_total = models.PositiveSmallIntegerField(
        'Total EB',
        blank=True,
        null=True,
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
    fb_total = models.DecimalField(
        'Total FB',
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        default=0
    )
    total_pieces = models.PositiveSmallIntegerField(
        'Total Piezas',
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
    total_bunches = models.IntegerField(
        'Total de ramos',
        blank=True,
        null=True,
        default=0
    )
    po_number = models.CharField(
        'Número PO',
        max_length=50,
        blank=True,
        null=True
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

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.marking:
            self.marking = self.marking.upper()
        if self.num_invoice:
            self.num_invoice = self.num_invoice.upper()
        if self.po_number:
            self.po_number = self.po_number.upper()
        if self.awb:
            self.awb = self.awb.upper()
        if self.dae_export:
            self.dae_export = self.dae_export.upper()
        if self.hawb:
            self.hawb = self.hawb.upper()
        if self.cargo_agency:
            self.cargo_agency = self.cargo_agency.upper()
        super().save(*args, **kwargs)

    @property
    def total_invoice(self):
        if self.type_document == 'FAC_VENTA':
            return self.total_price + self.total_margin

        return self.total_price

    @property
    def days_to_due(self):
        if self.due_date:
            return (self.due_date - self.date).days
        return None

    @property
    def is_dued(self):
        if self.due_date:
            return self.due_date.date() < datetime.now().date()
        return False

    @property
    def days_overdue(self):
        if self.due_date and self.is_dued:
            return (datetime.now().date() - self.due_date.date()).days
        return 0

    @classmethod
    def get_next_invoice_number(cls):
        last_invoice = cls.objects.filter(type_document='FAC_VENTA').last()

        if last_invoice:
            return last_invoice.num_invoice + 1
        return 1

    @classmethod
    def get_next_sale_consecutive(cls):
        last_purchase = cls.objects.filter(
            type_document='FAC_VENTA',
        ).order_by('-id').first()

        if last_purchase is None or last_purchase.consecutive is None:
            return 1

        return last_purchase.consecutive + 1

    @classmethod
    def get_next_purchase_consecutive(cls):
        last_bill = cls.objects.filter(
            type_document='FAC_COMPRA',
        ).order_by('-id').first()

        if last_bill is None or last_bill.consecutive is None:
            return 1

        return last_bill.consecutive + 1

    @classmethod
    def get_by_type(cls, type_document):
        return cls.objects.filter(type_document=type_document, is_active=True)

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
        eb_total = 0
        qb_total = 0
        hb_total = 0
        total_stem_flower = 0
        total_bunches = 0

        for invoice_item in InvoiceItems.get_invoice_items(invoice):
            InvoiceItems.rebuild_invoice_item(invoice_item)

        for invoice_item in InvoiceItems.get_invoice_items(invoice):
            total_price += invoice_item.line_price * invoice_item.quantity
            total_margin += invoice_item.line_margin * invoice_item.quantity
            total_stem_flower += invoice_item.tot_stem_flower
            total_bunches += invoice_item.total_bunches

            if invoice_item.box_model == 'EB':
                eb_total += invoice_item.quantity
            elif invoice_item.box_model == 'QB':
                qb_total += invoice_item.quantity
            elif invoice_item.box_model == 'HB':
                hb_total += invoice_item.quantity

        invoice.eb_total = eb_total
        invoice.qb_total = qb_total
        invoice.hb_total = hb_total
        invoice.total_margin = total_margin
        invoice.tot_stem_flower = total_stem_flower
        # FB = HB×(1/2) + QB×(1/4) + EB×(1/8)
        fb_calc = (hb_total * 0.5) + (qb_total * 0.25) + (eb_total * 0.125)
        invoice.fb_total = fb_calc
        invoice.total_price = total_price
        invoice.total_bunches = total_bunches

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
    total_bunches = models.IntegerField(
        'Total de ramos',
        blank=True,
        null=True,
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
    line_commission = models.DecimalField(
        'Comisión',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    @classmethod
    def get_invoice_items(cls, invoice):
        return cls.objects.filter(
            invoice=invoice,
            is_active=True
        )

    @classmethod
    def get_by_parent(cls, invoice):
        return cls.objects.filter(
            invoice=invoice,
            is_active=True
        )

    @classmethod
    def rebuild_invoice_item(cls, invoice_item):
        loggin_event(f"Reconstruyendo item de factura {invoice_item.id}")
        line_price = 0
        line_margin = 0
        tot_stem_flower = 0
        total_bunches = 0

        for oitm in InvoiceBoxItems.get_box_items(invoice_item):
            line_price += oitm.qty_stem_flower * oitm.stem_cost_price
            line_margin += oitm.profit_margin * oitm.qty_stem_flower
            tot_stem_flower += oitm.qty_stem_flower
            total_bunches += oitm.total_bunches

        invoice_item.line_price = line_price * invoice_item.quantity
        invoice_item.line_margin = line_margin * invoice_item.quantity
        invoice_item.line_total = (
            (line_price * invoice_item.quantity)
            + (line_margin * invoice_item.quantity)
        )
        invoice_item.tot_stem_flower = tot_stem_flower * \
            invoice_item.quantity  # Multiplicar por quantity
        invoice_item.total_bunches = total_bunches * \
            invoice_item.quantity  # Multiplicar por quantity
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
    commission = models.DecimalField(
        'Comisión',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )
    total_bunches = models.IntegerField(
        'Total de ramos',
        blank=True,
        null=True,
        default=0
    )
    stems_bunch = models.IntegerField(
        'Cantidad de tallos por ramo',
        blank=True,
        null=True,
        default=0
    )

    @property
    def total_price(self):
        return self.stem_cost_price * self.qty_stem_flower

    @property
    def unit_price(self):
        return self.stem_cost_price + self.profit_margin

    @property
    def total_price_with_margin(self):
        """Total del producto con margen incluido"""
        return self.unit_price * self.qty_stem_flower

    @property
    def total_price_with_margin_and_quantity(self):
        """Total del producto con margen incluido
        multiplicado por la cantidad de cajas"""
        return self.total_price_with_margin * self.invoice_item.quantity

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
