from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from common import BaseModel
from partners.models import Partner
from products.models import Product


BOX_CHOICES = (
    ('HB', 'HB'),
    ('QB', 'QB'),
    ('FB', 'FB')
)


class StockDay(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    date = models.DateField(
        'Fecha',
        unique=True
    )

    def get_stock_day(self, date):
        try:
            return self.objects.get(
                date=date
            )
        except ObjectDoesNotExist:
            return None

    @classmethod
    def disable(cls, stock_day):
        stock_day.is_active = False
        stock_day.save()

    @classmethod
    def get_by_id(cls, stock_day_id):
        try:
            return cls.objects.get(
                pk=stock_day_id
            )
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return str(self.date)


class StockDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    stock_day = models.ForeignKey(
        StockDay,
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField(
        'Cantidad Cajas',
        default=0,
        help_text='Cantidad de cajas'
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
    def get_by_id(cls, stock_detail_id):
        try:
            return cls.objects.get(
                pk=stock_detail_id
            )
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_by_stock_day(cls, stock_day):
        return cls.objects.filter(
            stock_day=stock_day,
            is_active=True
        )

    @classmethod
    def get_partner_by_stock_day(cls, stock_day):
        partners = cls.objects.filter(
            stock_day=stock_day,
            is_active=True
        ).values('partner').distinct()
        partners = set([i['partner'] for i in partners])
        return [Partner.get_partner_by_id(i) for i in partners]

    @classmethod
    def get_total_boxes_by_model(cls, stock_day, box_model):
        stock_detail = cls.objects.filter(
            stock_day=stock_day,
            is_active=True
        )
        boxes = 0
        for s_detail in stock_detail:
            box = BoxItems.get_box_items(s_detail)
            if box and s_detail.box_model == box_model:
                boxes += 1
        return boxes

    @classmethod
    def get_stock_day_partner(cls, stock_day, partner):
        return cls.objects.filter(
            stock_day=stock_day,
            partner=partner,
            is_active=True
        )

    @classmethod
    def disable_stock_detail(cls, stock_day, partner):
        stock_detail = cls.get_stock_day_partner(stock_day, partner)
        for i in stock_detail:
            i.is_active = False
            i.save()
            box_items = BoxItems.get_box_items(i)
            for j in box_items:
                j.is_active = False
                j.save()

    def __str__(self):
        return '{}'.format(
            self.stock_day
        )

    @classmethod
    def rebuild_stock_detail(cls, stock_detail):
        box_items = BoxItems.get_box_items(stock_detail)
        total_stem_flower = 0
        total_cost_price = 0
        total_margin = 0
        for box in box_items:
            total_stem_flower += box.qty_stem_flower
            total_cost_price += box.stem_cost_price
            total_margin += box.profit_margin

        stock_detail.tot_stem_flower = total_stem_flower
        stock_detail.tot_cost_price_box = total_cost_price
        stock_detail.profit_margin = total_margin
        stock_detail.save()


class BoxItems(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    stock_detail = models.ForeignKey(
        StockDetail,
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
    def get_by_id(cls, box_id):
        try:
            return cls.objects.get(
                pk=box_id
            )
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_box_items(cls, stock_detail):
        return cls.objects.filter(
            stock_detail=stock_detail,
            is_active=True
        )

    def __str__(self):
        return '{}'.format(
            self.product.name
        )
