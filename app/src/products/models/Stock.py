from django.db import models
from common import BaseModel
from partners.models import Partner
from products.models import Product


BOX_CHOICES = (
    ('hb', 'HB'),
    ('qb', 'QB'),
    ('fb', 'FB')
)


class StockDay(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    date = models.DateField(
        'Fecha',
        unique=True
    )

    def __str__(self):
        return self.date


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
    length = models.CharField(
        'Largo',
        max_length=255
    )
    quantity = models.IntegerField(
        'Cantidad',
        default=0,
        help_text='Cantidad de cajas'
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
    cost_price = models.DecimalField(
        'Precio de costo',
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return '{} {} {} {}'.format(
            self.product.name,
            self.color,
            self.length,
            self.quantity
        )
