from common import BaseModel
from django.db import models
from trade.models import Invoice


METHOD_CHOICES = [
    ('TRANSF', 'TRANSFERENCIA'),
    ('CHEQUE', 'CHEQUE'),
    ('EFECTIVO', 'EFECTIVO'),
    ('OTRO', 'OTRO'),
    ('TC', 'TARJETA DE CRÉDITO'),
    ('NC', 'NOTA DE CRÉDITO')
]


class Payment(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    invoices = models.ManyToManyField(
        'trade.Invoice'
    )
    date = models.DateField(
        'Fecha de pago'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=10,
        decimal_places=2
    )
    method = models.CharField(
        'Metodo de pago',
        max_length=50,
        default='OTRO'
    )
    bank = models.CharField(
        'Banco',
        max_length=50,
        blank=True,
        null=True
    )
    nro_account = models.CharField(
        'Nro de Cuenta',
        max_length=50,
        blank=True,
        null=True
    )
    nro_operation = models.CharField(
        'Nro de Operación',
        max_length=50,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Pago {self.id}"