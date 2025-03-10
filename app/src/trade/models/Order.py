from django.db import models
from products.models import Product, StockDay, StockDetail
from common import BaseModel
from partners.models import Partner

STATUS_CHOICES = (
    ('PENDIENTE', 'PENDIENTE'),
    ('CONFIRMADO', 'CONFIRMADO'),
    ('MODIFICADO', 'MODIFICADO'),
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


# -----------------------------------------------------------------------------
# MODELO DE ORDENES
# -----------------------------------------------------------------------------

class Order(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    stock_day = models.ForeignKey(
        StockDay,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
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
    total_stem_flower = models.PositiveSmallIntegerField(
        'Total Tallos',
        default=0,
        blank=True,
        null=True
    )

    @classmethod
    def get_order_by_id(cls, id_order):
        try:
            return cls.objects.get(pk=id_order)
        except cls.DoesNotExist:
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
    def get_purchases_by_stock_day(cls, stock_day):
        return cls.objects.filter(
            stock_day=stock_day,
            type_document='ORD_COMPRA',
            is_active=True,
        )

    @classmethod
    def get_by_parent_order(cls, sale_order):
        return cls.objects.filter(
            parent_order=sale_order,
            is_active=True
        )

    @classmethod
    def disable_order_items(cls, order):
        order_items = OrderItems.get_by_order(order.pk)
        for order_item in order_items:
            OrderItems.disable_order_item(order_item)

    @classmethod
    def rebuild_totals(self, order):
        total_price = 0
        qb_total = 0
        hb_total = 0
        total_stem_flower = 0
        for order_item in OrderItems.get_by_order(order):
            total_price += order_item.line_total
            total_stem_flower += order_item.tot_stem_flower
            if order_item.box_model == 'QB':
                qb_total += 1
            elif order_item.box_model == 'HB':
                hb_total += 1

        order.total_price = total_price
        order.qb_total = qb_total
        order.hb_total = hb_total
        order.total_stem_flower = total_stem_flower
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
    quantity = models.DecimalField(
        'Precio de costo Caja',
        max_digits=10,
        decimal_places=2,
        default=0.00
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
    def get_by_supplier(cls, order, supplier):
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
    def disable_order_item(cls, order_item):
        order_item.is_active = False
        order_item.save()

        order_box_items = OrderBoxItems.get_box_items(order_item)
        for box_item in order_box_items:
            box_item.is_active = False
            box_item.save()

    @classmethod
    def rebuild_order_item(cls, stock_detail):
        box_items = OrderBoxItems.get_box_items(stock_detail)
        total_stem_flower = 0
        line_margin = 0
        line_total = 0
        for box_item in box_items:
            total_stem_flower += box_item.qty_stem_flower
            line_margin += (box_item.profit_margin * box_item.qty_stem_flower)
            line_total += (
                box_item.qty_stem_flower * 
                (box_item.stem_cost_price + box_item.profit_margin)
            )

        stock_detail.tot_stem_flower = total_stem_flower
        stock_detail.line_margin = line_margin
        stock_detail.line_total = line_total
        stock_detail.line_price = line_total - line_margin
        stock_detail.save()


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

    @classmethod
    def get_box_items(cls, order_item):
        return cls.objects.filter(
            order_item=order_item,
            is_active=True
        )

    @classmethod
    def rebuild_order_item(cls, order_item):
        total_stem_flower = 0
        total_cost_price = 0
        total_margin = 0
        for box in cls.get_box_items(order_item):
            total_stem_flower += box.qty_stem_flower
            total_cost_price += box.stem_cost_price
            total_margin += box.profit_margin

        order_item.tot_stem_flower = total_stem_flower
        order_item.line_price = total_cost_price
        order_item.line_margin = total_margin
        order_item.line_total = total_cost_price * total_margin
        order_item.save()
