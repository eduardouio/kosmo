from django.db import models
from common import BaseModel
from accounts.models import CustomUserModel

ROLE_CHOICES = (
    ('ADMINISTRATIVO', 'ADMINISTRATIVO'),
    ('TECNICO', 'TECNICO'),
)


class License(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    license_key = models.CharField(
        'clave de licencia',
        max_length=250, unique=True
    )
    activated_on = models.DateTimeField(
        'activada el',
        null=True,
        blank=True
    )
    expires_on = models.DateTimeField(
        'expira el',
        null=True,
        blank=True
    )
    enterprise = models.CharField(
        'Empresa',
        max_length=50,
        default='KOSMOFLOWERS'
    )
    is_active = models.BooleanField(
        'Activo?',
        default=False
    )
    url_server = models.URLField(
        'URL del servidor',
        null=True,
        blank=True
    )
    user = models.ForeignKey(
        CustomUserModel,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return 'Licencia de {}'.format(self.user.email)
