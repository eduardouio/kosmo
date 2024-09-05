from django.db import models
from common import BaseModel


class Product(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    code = models.CharField(
        'Codigo',
        max_length=50,
        unique=True
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    image = models.ImageField(
        'Imagen',
        upload_to='products/',
        blank=True,
        null=True
    )
    variety = models.CharField(
        'Variedad',
        max_length=255
    )
    default_rend = models.DecimalField(
        'Rendimiento por defecto',
        max_digits=10,
        decimal_places=2,
        default=0.06,
        help_text='todo item tiene un rendimiento de 0.06 usd'
    )

    def __str__(self):
        return self.name
