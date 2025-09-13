from django.db import models
from trade.models import Invoice
from common.BaseModel import BaseModel

NC_STATUS = (
    ('APLICADO', 'APLICADO'),
    ('ANULADO', 'ANULADO')
    )

SERIES = (
    ('400', '400'),
)


class CreditNote(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    serie = models.CharField(
        'Serie',
        max_length=5,
        blank=True,
        null=True,
        default=None,
        choices=SERIES
    )
    consecutive = models.PositiveSmallIntegerField(
        'Consecutivo',
        blank=True,
        null=True,
        default=None
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        'Estado',
        max_length=10,
        choices=NC_STATUS,
        default='APLICADO'
    )
    id_payment = models.PositiveIntegerField(
        'ID del pago asociado',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del pago asociado a la nota de crédito, 0 si no hay pago asociado.'
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

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.num_credit_note:
            self.num_credit_note = self.num_credit_note.upper()
        if self.reason:
            self.reason = self.reason.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.invoice) + ' ' + str(self.amount)


class CreditNoteDetail(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    credit_note = models.ForeignKey(
        CreditNote,
        on_delete=models.CASCADE
    )
    description = models.CharField(
        'Descripción',
        max_length=200
    )
    quantity = models.IntegerField(
        'Cantidad'
    )
    unit_price = models.DecimalField(
        'Precio unitario',
        max_digits=10,
        decimal_places=2
    )
    total_price = models.DecimalField(
        'Precio total',
        max_digits=10,
        decimal_places=2
    )

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.description:
            self.description = self.description.upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.description) + ' ' + str(self.total_price)