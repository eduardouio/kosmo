from django.db import models
from common import BaseModel
from django.core.exceptions import ObjectDoesNotExist


class Product(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    name = models.CharField(
        'Nombre',
        max_length=255,
    )
    variety = models.CharField(
        'Variedad',
        max_length=255,
    )
    image = models.ImageField(
        'Imagen',
        upload_to='products/',
        blank=True,
        null=True
    )
    colors = models.CharField(
        'Colores Seprados por Comas',
        max_length=255,
        blank=True,
        null=True,
        default='NO DEFINIDO'
    )
    default_profit_margin = models.DecimalField(
        'Rendimiento por defecto',
        max_digits=10,
        decimal_places=2,
        default=0.06,
        help_text='todo item tiene un rendimiento de 0.06 usd'
    )

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.name:
            self.name = self.name.upper()
        if self.variety:
            self.variety = self.variety.upper()
        if self.colors:
            self.colors = self.colors.upper()
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('name', 'variety')

    @classmethod
    def get_by_variety(cls, name):
        flower = cls.objects.filter(variety__icontains=name).first()
        if not flower:
            return None

        return flower

    def __str__(self):
        return self.name + ' - ' + self.variety
