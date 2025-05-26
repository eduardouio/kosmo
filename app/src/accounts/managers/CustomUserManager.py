from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el correo electrónico y la contraseña proporcionados.
        """
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')
        email = self.normalize_email(email)
        # Asegurarse de que 'phone' se maneje correctamente si se pasa en extra_fields
        # o como un argumento nombrado.
        phone = extra_fields.pop('phone', None)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Crea y guarda un superusuario con el correo electrónico y la contraseña proporcionados.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        # No es necesario llamar a self.normalize_email aquí, create_user lo hará.
        # No es necesario llamar a user.set_password() y user.save() aquí, create_user lo hará.
        return self.create_user(email, password, **extra_fields)