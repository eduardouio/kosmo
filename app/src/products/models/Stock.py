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


# los stoks son por tipo de caja si son dos tipos de caja se crean dos
# registros aunque sean del mismo producto
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
    stem_cost_price_box = models.DecimalField(
        'Precio de costo Tallo',
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    @classmethod
    def get_total_boxes_by_model(cls, stock_day, box_model):
        stock_detail = cls.objects.filter(
            stock_day=stock_day
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
            partner=partner
        )

    def __str__(self):
        return '{}'.format(
            self.stock_day
        )


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

    @classmethod
    def get_box_items(cls, stock_detail):
        return cls.objects.filter(
            stock_detail=stock_detail
        )

    def __str__(self):
        return '{}'.format(
            self.product.name
        )
