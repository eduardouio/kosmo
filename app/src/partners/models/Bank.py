from django.db import models
from common import BaseModel
from .Partner import Partner


class Bank(BaseModel):
    id = models.AutoField(
        primary_key=True
     )
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

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.owner:
            self.owner = self.owner.upper()
        if self.id_owner:
            self.id_owner = self.id_owner.upper()
        if self.account_number:
            self.account_number = self.account_number.upper()
        if self.bank_name:
            self.bank_name = self.bank_name.upper()
        if self.swift_code:
            self.swift_code = self.swift_code.upper()
        if self.iban:
            self.iban = self.iban.upper()
        super().save(*args, **kwargs)

    @classmethod
    def get_by_partner(cls, partner):
        return cls.objects.filter(partner=partner)

    def __str__(self):
        if self.national_bank:
            return f'Nac: {self.bank_name}'
        return f'Ext: {self.bank_name}'
