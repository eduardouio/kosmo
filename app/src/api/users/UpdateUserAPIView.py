from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, parsers
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.models.CustomUserModel import CustomUserModel
from common.AppLoger import loggin_event


class UpdateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [
        parsers.JSONParser,
        parsers.FormParser,
        parsers.MultiPartParser,
    ]

    def post(self, request):
        user = request.user  # Usuario autenticado
        loggin_event(
            f"UpdateUserAPIView POST por {getattr(user, 'email', user)}"
        )
        data = request.data
        action = data.get('action') or 'update_profile'

        if action == 'change_password':
            return self._change_password(user, data)

        return self._update_profile(user, request)

    @transaction.atomic
    def _update_profile(self, user: CustomUserModel, request):
        data = request.data
        picture = request.FILES.get('picture')

        # Campos permitidos
        allowed_fields = ['first_name', 'last_name', 'phone', 'notes', 'email']
        updates = {}

        def clean_val(v):
            if v is None:
                return None
            if isinstance(v, str):
                v = v.strip()
                if v in ('None', 'null', 'undefined'):
                    return ''
            return v

        for f in allowed_fields:
            if f in data:
                updates[f] = clean_val(data.get(f))

        # Validaciones
        email = updates.get('email')
        if email and email != user.email:
            exists = (
                CustomUserModel.objects.filter(email=email)
                .exclude(pk=user.pk)
                .exists()
            )
            if exists:
                loggin_event(
                    f"Intento de cambiar email a existente: {email}"
                )
                return Response(
                    {'detail': 'El correo ya está en uso.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Aplicar cambios
        for k, v in updates.items():
            setattr(user, k, v)

        if picture is not None:
            user.picture = picture

        try:
            user.full_clean()
        except ValidationError as e:
            loggin_event(f"Error de validación al actualizar perfil: {e}")
            return Response(
                {'detail': e.message_dict},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.save()
        loggin_event("Perfil actualizado correctamente")

        return Response(
            {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'notes': user.notes,
                'picture': (
                    user.picture.url
                    if getattr(user, 'picture', None)
                    and getattr(user.picture, 'url', None)
                    else None
                ),
            },
            status=status.HTTP_200_OK,
        )

    @transaction.atomic
    def _change_password(self, user: CustomUserModel, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            loggin_event("Campos de contraseña incompletos")
            return Response(
                {'detail': 'Todos los campos de contraseña son obligatorios.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            loggin_event("Contraseña actual incorrecta")
            return Response(
                {'detail': 'La contraseña actual es incorrecta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            loggin_event("No coinciden las nuevas contraseñas")
            return Response(
                {'detail': 'Las contraseñas no coinciden.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 8:
            loggin_event("Nueva contraseña menor a 8 caracteres")
            return Response(
                {
                    'detail': (
                        'La nueva contraseña debe tener al menos '
                        '8 caracteres.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        loggin_event("Contraseña actualizada correctamente")

        return Response(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=status.HTTP_200_OK,
        )
