from django.db import models
from products.models import Product, StockDay, StockDetail
from common import BaseModel
from common.AppLoger import loggin_event
from partners.models import Partner


STATUS_CHOICES = (
    ('PENDIENTE', 'PENDIENTE'),
    ('CONFIRMADO', 'CONFIRMADO'),
    ('MODIFICADO', 'MODIFICADO'),
    ('FACTURADO', 'FACTURADO'),
    ('CANCELADO', 'CANCELADO'),
    ('PROMESA', 'PROMESA')
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

SERIES = (
    ('100', '100'),
    ('200', '200'),
)


# -----------------------------------------------------------------------------
# MODELO DE ORDENES
# -----------------------------------------------------------------------------

class Order(BaseModel):
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
    stock_day = models.ForeignKey(
        StockDay,
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    date = models.DateTimeField(
        'Fecha',
        auto_now=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.RESTRICT,
        help_text='C customer S supplier'
    )
    type_document = models.CharField(
        'Tipo de Documento',
        max_length=50,
        choices=TYPE_DOCUMENT_CHOICES
    )
    parent_order = models.ForeignKey(
        'self',
        on_delete=models.RESTRICT,
        blank=True,
        null=True,
    )
    num_order = models.CharField(
        'PO Socio',
        max_length=50,
        blank=True,
        null=True,
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
        default=0
    )
    hb_total = models.PositiveSmallIntegerField(
        'Total HB',
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
    total_stem_flower = models.PositiveSmallIntegerField(
        'Total Tallos',
        default=0,
        blank=True,
        null=True
    )
    is_invoiced = models.BooleanField(
        'Facturado',
        default=False
    )
    id_invoice = models.PositiveIntegerField(
        'Factura',
        blank=True,
        null=True,
        default=0
    )
    num_invoice = models.CharField(
        'No Factura',
        max_length=50,
        blank=True,
        null=True,
        default=None
    )

    @property
    def total_order(self):
        if self.type_document == 'ORD_COMPRA':
            return self.total_price

        return self.total_price + self.total_margin

    @property
    def consecutive_text(self):
        consecutive = self.consecutive if self.consecutive else 0
        return str(consecutive).zfill(6)

    @classmethod
    def get_order_by_id(cls, id_order):
        try:
            return cls.objects.get(pk=id_order)
        except cls.DoesNotExist:
            loggin_event(f"Pedido {id_order} nop existe", error=True)
            return None

    def __str__(self):
        return f"Pedido {self.id} - {self.partner.name}"

    @classmethod
    def get_sales_by_stock_day(cls, stock_day):
        return cls.objects.filter(
            stock_day=stock_day,
            type_document='ORD_VENTA',
            is_active=True,
        )

    @classmethod
    def get_purchases_by_stock_day(cls, id_stock_day):
        return cls.objects.filter(
            stock_day=id_stock_day,
            type_document='ORD_COMPRA',
            is_active=True,
        )

    @classmethod
    def get_next_sale_consecutive(cls):
        consecutive = cls.objects.filter(
            type_document='ORD_VENTA',
        ).order_by('-id').first().consecutive

        if consecutive is None:
            return 1

        return consecutive + 1

    @classmethod
    def get_next_purchase_consecutive(cls):
        return cls.objects.filter(
            type_document='ORD_COMPRA',
        ).order_by('-id').first().consecutive + 1

    @classmethod
    def get_by_parent_order(cls, sale_order):
        sup_orders = cls.objects.filter(
            parent_order=sale_order,
            is_active=True
        )
        if len(sup_orders):
            return sup_orders

        loggin_event(
            f"La orden {sale_order.pk} no tiene ordenes de proveedor", True)
        return None

    @property
    def total_purchase_price(self):
        total = 0
        for order_item in OrderItems.get_by_order(self):
            total += order_item.line_price
        return total

    @property
    def total_sale_price(self):
        total = 0
        for order_item in OrderItems.get_by_order(self):
            total += order_item.line_total
        return total

    @classmethod
    def disable_order_items(cls, order):
        loggin_event(f"Desactivando items de orden {order.id}")
        order_items = OrderItems.get_by_order(order.pk)
        for order_item in order_items:
            order_item.is_active = False
            order_item.save()
            OrderBoxItems.disable_by_order_items(order_item)

    @classmethod
    def rebuild_totals(self, order):
        loggin_event(f"Reconstruyendo totales de orden {order.id}")
        total_price = 0
        total_margin = 0
        total_order = 0
        qb_total = 0
        hb_total = 0
        total_stem_flower = 0

        for order_item in OrderItems.get_by_order(order):
            OrderItems.rebuild_order_item(order_item)

        for order_item in OrderItems.get_by_order(order):
            total_price += order_item.line_price
            total_margin += order_item.line_margin
            total_order += order_item.line_total
            total_stem_flower += order_item.tot_stem_flower

            if order_item.box_model == 'QB':
                qb_total += (order_item.quantity)
            elif order_item.box_model == 'HB':
                hb_total += (order_item.quantity)

        order.qb_total = qb_total
        order.hb_total = hb_total
        order.fb_total = ((qb_total / 2) + hb_total) / 2
        order.total_margin = total_margin
        order.total_stem_flower = total_stem_flower
        order.total_price = total_price
        order.total_margin = total_margin
        order.save()


# -----------------------------------------------------------------------------
# MODELO DE ITEMS DE ORDEN
# -----------------------------------------------------------------------------


class OrderItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    id_stock_detail = models.PositiveSmallIntegerField(
        'Detalle de Stock',
        blank=True,
        null=True,
        default=0,
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
    tot_stem_flower = models.IntegerField(
        'Unds Tallos',
        default=0,
        help_text='Cantidad de tallos de flor'
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
    is_deleted = models.BooleanField(
        'Eliminado',
        default=False
    )
    is_modified = models.BooleanField(
        'Modificado',
        default=False
    )
    parent_order_item = models.PositiveIntegerField(
        'Item de orden padre',
        blank=True,
        null=True,
        default=0
    )

    @property
    def qb_total(self):
        if self.box_model == 'QB':
            return self.quantity
        return 0

    @property
    def hb_total(self):
        if self.box_model == 'HB':
            return self.quantity
        return 0

    @classmethod
    def get_by_id(cls, id_order_item):
        try:
            order_item = cls.objects.get(pk=id_order_item)
            if order_item.is_active:
                return order_item
            return None

        except cls.DoesNotExist:
            loggin_event(
                f"Item de orden {id_order_item} no existe", error=True
            )
            return None

    @classmethod
    def get_suppliers_by_order(cls, order):
        partners = cls.objects.filter(order=order).values_list(
            'stock_detail__partner', flat=True
        ).distinct()

        if partners:
            return [Partner.get_by_id(x) for x in set(partners)]

        return []

    @classmethod
    def get_by_supplier(cls, order, supplier):
        """Obtiene los orders items de un pedido para un proveedor"""
        orders_items = cls.get_by_order(order)
        order_items_related = []
        for order_item in orders_items:
            stock_detail = StockDetail.get_by_id(order_item.id_stock_detail)
            if stock_detail.partner == supplier:
                order_items_related.append(order_item)
        return order_items_related

    @classmethod
    def get_by_order(cls, order):
        return cls.objects.filter(order=order, is_active=True)

    @classmethod
    def get_by_stock_detail(cls, id_stock_detail, order):
        return cls.objects.filter(
            order=order,
            id_stock_detail=id_stock_detail,
            is_active=True
        )

    @classmethod
    def disable_by_order(cls, order):
        order_items = cls.get_by_order(order)
        for order_item in order_items:
            order_item.is_active = False
            order_item.save()
            OrderBoxItems.disable_by_order_items(order_item)

    @classmethod
    def disable_by_order_item(cls, order_item):
        order_item.is_active = False
        order_item.save()
        OrderBoxItems.disable_by_order_items(order_item)

    @classmethod
    def rebuild_order_item(cls, order_item):
        loggin_event(f"Reconstruyendo item de orden {order_item.id}")
        total_stem_flower = 0
        total_price = 0
        total_margin = 0

        for box in OrderBoxItems.get_box_items(order_item):
            total_stem_flower += box.qty_stem_flower * order_item.quantity
            total_price += (box.stem_cost_price * box.qty_stem_flower)
            total_margin += (box.profit_margin * box.qty_stem_flower)

        order_item.tot_stem_flower = total_stem_flower
        order_item.line_price = total_price * order_item.quantity
        order_item.line_margin = total_margin * order_item.quantity
        order_item.line_total = order_item.line_price + order_item.line_margin
        order_item.save()

# -----------------------------------------------------------------------------
# MODELO DE CAJAS DE ORDEN ITEM
# -----------------------------------------------------------------------------


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
    def stem_cost_total(self):
        return self.stem_cost_price + self.profit_margin

    @property
    def stem_cost_total_price(self):
        return self.stem_cost_price * self.qty_stem_flower

    @property
    def stem_cost_total_sale(self):
        return self.stem_cost_total * self.qty_stem_flower

    @classmethod
    def get_by_order_item(cls, order_item):
        return cls.objects.filter(order_item=order_item, is_active=True)

    @classmethod
    def disable_by_order_items(cls, order_item):
        box_items = cls.get_box_items(order_item)
        for box_item in box_items:
            box_item.is_active = False
            box_item.save()

    @classmethod
    def get_box_items(cls, order_item):
        return cls.objects.filter(
            order_item=order_item,
            is_active=True
        )

    @classmethod
    def rebuild_order_item(cls, order_item):
        loggin_event(f"Reconstruyendo item de orden {order_item.id}")
        line_t_stem_flower = 0
        line_cost_price = 0
        line_margin = 0
        for box in cls.get_box_items(order_item):
            line_t_stem_flower += box.qty_stem_flower
            line_cost_price += box.stem_cost_price * box.qty_stem_flower
            line_margin += box.profit_margin * box.qty_stem_flower

        order_item.tot_stem_flower = line_t_stem_flower * order_item.quantity
        order_item.line_price = line_cost_price * order_item.quantity
        order_item.line_margin = line_margin * order_item.quantity
        order_item.line_total = (
            (order_item.line_price * order_item.quantity)
            + (order_item.line_margin * order_item.quantity)
        )
        order_item.save()
