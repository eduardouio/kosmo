from common import BaseModel
from django.db import models
from trade.models import Invoice


METHOD_CHOICES = [
    ('transfer', 'Transferencia'),
    ('check', 'Cheque'),
    ('cash', 'Efectivo'),
    ('other', 'Otro'),
    ('credit_card', 'Tarjeta de Crédito'),
    ('credit_note', 'Nota de Crédito')
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
        max_length=50
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
    evidence = models.FileField(
        'Comprobante',
        upload_to='payments',
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Pago {self.id} - Factura {self.invoice.id}"