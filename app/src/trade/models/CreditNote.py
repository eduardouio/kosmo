from django.db import models
from trade.models import Invoice


class CreditNote(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    num_credit_note = models.CharField(
        'Numero de nota de crédito',
        max_length=50
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )
    date = models.DateField(
        'Fecha de la nota de crédito'
    )
    amount = models.DecimalField(
        'Monto',
        max_digits=10,
        decimal_places=2
    )
    reason = models.TextField(
        'Motivo de la nota de crédito'
    )

    def __str__(self):
        return self.invoice + ' ' + self.amount
