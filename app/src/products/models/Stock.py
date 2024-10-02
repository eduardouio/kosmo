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
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )
    color = models.CharField(
        'Color',
        max_length=255
    )
    length = models.PositiveSmallIntegerField(
        'Largo CM',
    )
    box_quantity = models.IntegerField(
        'Cantidad Cajas',
        default=0,
        help_text='Cantidad de cajas'
    )
    qty_stem_flower = models.IntegerField(
        'Cant Tallos',
        default=0,
        help_text='Cantidad de tallos de flor'
    )
    box_model = models.CharField(
        'Tipo de caja',
        max_length=50,
        choices=BOX_CHOICES
    )
    stem_cost_price = models.DecimalField(
        'Precio de costo Tallo',
        max_digits=10,
        decimal_places=2
    )

    @classmethod
    def get_stock_day(cls, date):
        return cls.objects.filer(
            stock_day__date=date
        )

    @classmethod
    def get_stock_day_partner(cls, stock_day, partner):
        return cls.objects.filter(
            stock_day=stock_day,
            partner=partner
        )

    def __str__(self):
        return '{}'.format(
            self.product.name
        )
