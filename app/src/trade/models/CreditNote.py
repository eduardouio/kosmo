from django.db import models, transaction
from django.core.exceptions import ValidationError
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
    consecutive = models.PositiveIntegerField(
        'Consecutivo',
        blank=True,
        null=True,
        default=None,
        help_text='Consecutivo autogenerado dentro de la serie.'
    )
    num_credit_note = models.CharField(
        'Número Nota de Crédito',
        max_length=30,
        blank=True,
        null=True,
        default=None,
        help_text='Identificador legible Serie-Consecutivo.'
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
        help_text=(
            'Identificador del pago asociado a la nota de crédito, '
            '0 si no hay pago asociado.'
        )
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

    def clean(self):
        if self.amount and self.amount <= 0:
            raise ValidationError({'amount': 'El monto debe ser mayor a 0.'})
        if not self.invoice_id:
            raise ValidationError({'invoice': 'Debe seleccionar una factura.'})

    def save(self, *args, **kwargs):
        # Upper
        if self.reason:
            self.reason = self.reason.upper()

        generating_number = False
        if not self.pk:
            # Asignar serie por defecto si no viene
            if not self.serie:
                self.serie = SERIES[0][0]
            if self.consecutive is None:
                generating_number = True

        with transaction.atomic():
            if generating_number:
                # bloquear filas de la misma serie para evitar colisiones
                last = (
                    CreditNote.objects.select_for_update()
                    .filter(serie=self.serie)
                    .order_by('-consecutive')
                    .first()
                )
                self.consecutive = (
                    1 if not last or not last.consecutive
                    else last.consecutive + 1
                )
            # Construir número legible
            if self.serie and self.consecutive:
                self.num_credit_note = (
                    f'{self.serie}-{str(self.consecutive).zfill(6)}'
                )
            super().save(*args, **kwargs)

    @property
    def total_details(self):
        agg = self.creditnotedetail_set.aggregate(s=models.Sum('total_price'))
        return agg['s'] or 0

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
        if self.description:
            self.description = self.description.upper()
        # Autocalcular total si no se provee
        if self.unit_price is not None and self.quantity is not None:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.description) + ' ' + str(self.total_price)
