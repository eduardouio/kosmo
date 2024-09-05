from django.db import models
from common import BaseModel
from .Partner import Partner

COTACT_TYPE_CHOICES = [
    'commercial', 'Comercial',
    'financial', 'Financiero',
    'logistic', 'Logístico',
    'other', 'Otro'
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
        max_length=255
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

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Contacto'
        verbose_name_plural = 'Contactos'
        db_table = 'partner_contact'
        unique_together = ('partner', 'name')
