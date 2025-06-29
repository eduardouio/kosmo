from django.db import models
from .Partner import Partner
from common import BaseModel


class DAE(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )
    dae = models.CharField(
        'DAE',
        max_length=50,
        unique=True
    )
    awb = models.CharField(
        'MAWB',
        max_length=50,
        blank=True,
        null=True
    )
    hawb = models.CharField(
        'HAWB',
        max_length=50,
        blank=True,
        null=True
    )
    cargo_agency = models.CharField(
        'Agencia de Carga',
        max_length=50,
        blank=True,
        null=True
    )
    date_begin = models.DateField(
        'Fecha de Inicio',
    )
    date_end = models.DateField(
        'Fecha de Fin',
    )

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.dae:
            self.dae = self.dae.upper()
        if self.awb:
            self.awb = self.awb.upper()
        if self.hawb:
            self.hawb = self.hawb.upper()
        if self.cargo_agency:
            self.cargo_agency = self.cargo_agency.upper()
        super().save(*args, **kwargs)

    @classmethod
    def get_last_by_partner(cls, partner):
        daes = cls.objects.filter(partner=partner, is_active=True)
        if daes:
            return daes.latest('date_end')

    def __str__(self):
        return '{} {}'.format(self.dae, self.partner)
