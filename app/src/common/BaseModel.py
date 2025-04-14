"""
 Modelo base para todos los modelos de la aplicación, todos los modelos
    deben heredar de este modelo.

    Attributes:
        created_at (DateTime): Fecha de creación del registro.
        updated_at (DateTime): Fecha de actualización del registro.
        deleted_at (DateTime): Fecha de eliminación del registro.
        historical (HistoricalRecords): Registros históricos del modelo.

    Methods:
        save: Guarda el registro en la base de datos, 
              incluye el usuario creador y actualizador.
        get_user: Obtiene el usuario creador o actualizador del registro.

"""


from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ObjectDoesNotExist
from common.AppLoger import loggin_event

# django-crum
from crum import get_current_user

# Modelo de usuario Peronalizado
from accounts.models.CustomUserModel import CustomUserModel


class BaseModel(models.Model):

    notes = models.TextField(
        'notas',
        blank=True,
        default=None,
        null=True,
        help_text='Notas del registro.'
    )

    created_at = models.DateTimeField(
        'fecha de creación',
        auto_now_add=True,
        help_text='Fecha de creación del registro.'
    )

    updated_at = models.DateTimeField(
        'fecha de actualización',
        auto_now=True,
        help_text='Fecha de ultima actualización del registro.'
    )

    is_active = models.BooleanField(
        'activo',
        default=True,
        help_text='Estado del registro.'
    )

    id_user_created = models.PositiveIntegerField(
        'usuario creador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario creador del registro 0 es anonimo.'
    )

    id_user_updated = models.PositiveIntegerField(
        'usuario actualizador',
        default=0,
        blank=True,
        null=True,
        help_text='Identificador del usuario actualizador del registro.'
    )

    @property
    def user_creator(self):
        """Devuelve el usuario creador de la orden"""
        if self.id_user_created:
            user = CustomUserModel.get_by_id(self.id_user_created)
            if user:
                return user
        return None

    history = HistoricalRecords(inherit=True)

    def save(self, *args, **kwargs):
        loggin_event(
            f'Guardando registro {self.__class__.__name__} con id {self.pk}')
        user = get_current_user()

        if user is None:
            return super().save(*args, **kwargs)

        if not self.pk:
            self.id_user_created = user.pk

        self.id_user_updated = user.pk
        return super().save(*args, **kwargs)

    def get_create_user(self):
        '''Retorna el usuario creador del registro.'''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_created)
        except ObjectDoesNotExist:
            return None

    def get_update_user(self):
        '''Retorna el usuario ultimo en actualizar el registro '''
        try:
            return CustomUserModel.objects.get(pk=self.id_user_updated)
        except ObjectDoesNotExist:
            return None

    def get_by_id(self, id):
        """Devuelve el registro por id"""
        loggin_event(f'Buscando registro {self.__name__} con id {id}')
        try:
            result = self.objects.get(pk=id)
            if result.is_active:
                return result
            else:
                loggin_event("El registro no existe o fue eliminado")
                raise Exception("El registro no existe o fue eliminado")
        except ObjectDoesNotExist:
            return None

    def delete(self, id):
        """Marca el registro como eliminado"""
        loggin_event(f'Eliminando registro {self.__name__} con id {id}')
        try:
            instance = self.objects.get(pk=id)
            instance.is_active = False
            instance.save()
            return instance
        except ObjectDoesNotExist:
            return None
        except Exception as e:
            print(f"Error deleting instance: {e}")
            return None

    def get_all(self):
        """Devuelve todos los registros"""
        loggin_event(f'Buscando todos los registros {self.__name__}')
        return self.objects.filter(is_active=True)

    def get_all_with_inactive(self):
        """Devuelve todos los registros"""
        loggin_event(f'Buscando todos los registros {self.__name__}')
        return self.objects.all()

    def get_all_related(self):
        """Devuelve todos los registros activos del mismo tipo"""
        loggin_event(f'Buscando todos los registros {self.__class__.__name__}')
        return self.__class__.objects.filter(is_active=True)

    def get_all_inactive_related(self):
        """Devuelve todos los registros del mismo tipo, incluyendo inactivos"""
        loggin_event(f'Buscando todos los registros {self.__class__.__name__}')
        return self.__class__.objects.all()

    def get_all_related_with_inactive(self):
        """Devuelve todos los registros del mismo tipo incluyendo inactivos"""
        loggin_event(f'Buscando todos los registros {self.__class__.__name__}')
        return self.__class__.objects.all()

    @classmethod
    def get_by_id(cls, id):
        """Devuelve el registro por id"""
        loggin_event(f'Buscando registro {cls.__name__} con id {id}')
        try:
            result = cls.objects.get(pk=id)
            if result.is_active:
                return result
            else:
                loggin_event("El registro no existe o fue eliminado")
                raise Exception("El registro no existe o fue eliminado")
        except ObjectDoesNotExist:
            return None

    @classmethod
    def get_all(cls):
        loggin_event(f'Buscando todos los registros {cls.__name__}')
        return cls.objects.filter(is_active=True)

    @classmethod
    def get_all_inactive(cls):
        loggin_event(f'Buscando todos los registros inactivos {cls.__name__}')
        return cls.objects.filter(is_active=False)

    @classmethod
    def get_all_with_inactive(cls):
        loggin_event(f'Buscando todos los registros {cls.__name__}')
        return cls.objects.all()

    class Meta:
        abstract = True
        get_latest_by = 'created_at'
