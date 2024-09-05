from django.db import models
from common import BaseModel

PAYMENT_METHOD_CHOICES = [
    ('transfer', 'Transfer'),
    ('check', 'Check'),
    ('cash', 'Cash'),
    ('other', 'Other')
]

PARTNER_TYPE_CHOICES = [
    ('client', 'Cliente'),
    ('provider', 'Proveedor'),
]


# el cliente solo recibe las disponibilidades de los productos de ciertas
# fincas o proveedor de kosmo
class Partner(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    code = models.CharField(
        'Código',
        max_length=50,
        unique=True
    )
    business_tax_id = models.CharField(
        'RUC',
        max_length=15,
        unique=True
    )
    partner = models.ManyToManyField(
        "self",
        blank=True,
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    address = models.CharField(
        'Dirección',
        max_length=255
    )
    country = models.CharField(
        'País',
        max_length=50
    )
    city = models.CharField(
        'Ciudad',
        max_length=50
    )
    zip_code = models.CharField(
        'Código Postal',
        max_length=10
    )
    website = models.CharField(
        'Sitio Web',
        max_length=255,
        blank=True,
        null=True
    )
    credit_term = models.IntegerField(
        'Plazo de crédito',
        help_text="Tiempo de crédito en días, cero para prepago",
        default=0
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        null=True
    )
    skype = models.CharField(
        'Skype',
        max_length=50,
        blank=True,
        null=True
    )
    dispatch_address = models.CharField(
        'Dirección de Envío',
        max_length=255,
        blank=True,
        null=True
    )
    dispatch_days = models.PositiveIntegerField(
        'Días de Envío',
        blank=True,
        null=True
    )
    cargo_reference = models.CharField(
        'Referencia de Carga',
        max_length=255,
        blank=True,
        null=True
    )
    type_partner = models.CharField(
        'Tipo de Socio',
        max_length=50,
        choices=PARTNER_TYPE_CHOICES,
    )
    businnes_start = models.DateField(
        'Años en el mercado',
        blank=True,
        null=True
    )
    consolidate = models.BooleanField(
        'Consolidado',
        default=False
    )

    def __str__(self):
        if self.type_partner == 'client':
            return f'C: {self.name}'
        return f'S: {self.name}'
