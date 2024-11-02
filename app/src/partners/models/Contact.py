from django.db import models
from common import BaseModel
from .Partner import Partner

COTACT_TYPE_CHOICES = [
    'COMERCIAL', 'COMERCIAL',
    'FINANCIERO', 'FINANCIERO',
    'LOGISTICA', 'LOGÍSTICO',
    'OTRO', 'OTRO'
]


class Contact(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        'Nombre',
        max_length=255
    )
    position = models.CharField(
        'Cargo',
        max_length=255,
        blank=True,
        null=True
    )
    phone = models.CharField(
        'Teléfono',
        max_length=20,
        blank=True,
        null=True
    )
    email = models.EmailField(
        'Correo Electrónico',
        max_length=255,
        blank=True,
        null=True
    )
    is_principal = models.BooleanField(
        'Principal',
        default=False
    )

    @classmethod
    def get_by_partner(cls, partner):
        return cls.objects.filter(partner=partner)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('partner', 'name')
