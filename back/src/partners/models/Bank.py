from django.db import models
from common import BaseModel
from .Partner import Partner


class Bank(BaseModel):
    id = models.AutoField(primary_key=True)
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE,
        related_name='banks'
    )
    owner = models.CharField(
        'Propietario',
        max_length=255
    )
    id_owner = models.CharField(
        'DNI/RUC/CI',
        max_length=15
    )
    account_number = models.CharField(
        'Número de Cuenta',
        max_length=50
    )
    bank_name = models.CharField(
        'Nombre del Banco',
        max_length=100
    )
    swift_code = models.CharField(
        'Código SWIFT',
        max_length=50,
        blank=True,
        null=True
    )
    iban = models.CharField(
        'IBAN',
        max_length=50,
        blank=True,
        null=True
    )
    national_bank = models.BooleanField(
        'Banco Nacional?',
        default=True
    )

    def __str__(self):
        if self.national_bank:
            return f'Nac: {self.bank_name}'
        return f'Ext: {self.bank_name}'
