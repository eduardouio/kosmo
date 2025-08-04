from django.db import models
from common.BaseModel import BaseModel
from .Partner import Partner

COTACT_TYPE_CHOICES = (
    ('COMERCIAL', 'COMERCIAL'),
    ('FINANCIERO', 'FINANCIERO'),
    ('LOGISTICA', 'LOGÍSTICO'),
    ('GERENCIA', 'GERENCIA'),
    ('OTRO', 'OTRO'),
)


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
    contact_type = models.CharField(
        'Tipo de Contacto',
        max_length=20,
        choices=COTACT_TYPE_CHOICES,
        default='COMERCIAL'
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

    def save(self, *args, **kwargs):
        # Convertir campos de texto a mayúsculas
        if self.name:
            self.name = self.name.upper()
        if self.position:
            self.position = self.position.upper()
        if self.phone:
            self.phone = self.phone.upper()
        super().save(*args, **kwargs)

    @classmethod
    def get_by_partner(cls, partner):
        return cls.objects.filter(partner=partner)

    @classmethod
    def get_principal_by_partner(cls, partner):
        return cls.objects.filter(partner=partner, is_principal=True).first()

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('partner', 'name')
