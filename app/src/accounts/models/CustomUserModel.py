"""
    Modelos Personalizados de la Aplicación de Cuentas de Usuario.
    usamos el Correo Electrónico como nombre de usuario.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from accounts.managers import CustomUserManager


ROLE_CHOICES = (
    ('admin', 'Administrador'),
    ('sales', 'Ventas'),
)


class CustomUserModel(AbstractUser):
    username = None
    email = models.EmailField(
        'correo electrónico',
        unique=True
    )
    picture = models.ImageField(
        'imagen de perfil',
        upload_to='accounts/pictures',
        blank=True,
        help_text='Imagen de perfil del usuario.'
    )
    is_confirmed_mail = models.BooleanField(
        'correo electrónico confirmado',
        default=False,
        help_text='Estado de confirmación del correo electrónico.'
    )
    notes = models.TextField(
        'notas',
        blank=True
    )
    roles = models.CharField(
        'Role',
        choices=ROLE_CHOICES,
        default='sales',
        max_length=20
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    @classmethod
    def get(cls, email):
        try:
            return cls.objects.get(email=email)
        except ObjectDoesNotExist:
            return None

    def __str__(self):
        return self.email
