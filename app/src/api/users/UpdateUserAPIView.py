import json
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.models.CustomUserModel import CustomUserModel
from accounts.models.License import License
from common.AppLoger import loggin_event


class UpdateUserAPIView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user  # Usuario autenticado
        loggin_event(
            f"UpdateUserAPIView POST por {getattr(user, 'email', user)}"
        )
        data = self._get_request_data(request)
        action = data.get('action') or 'update_profile'

        if action == 'change_password':
            return self._change_password(user, data)

        if action == 'update_license':
            return self._update_license(user, data)

        # Acciones administrativas sobre otros usuarios (solo ADMINISTRADOR)
        if action == 'admin_toggle_active':
            return self._admin_toggle_active(request.user, data)

        if action == 'admin_reset_password':
            return self._admin_reset_password(request.user, data)

        return self._update_profile(user, request)

    def _get_request_data(self, request):
        content_type = request.META.get('CONTENT_TYPE', '')
        if 'application/json' in content_type:
            try:
                body = request.body.decode('utf-8') or '{}'
                return json.loads(body)
            except Exception:
                return {}
        # Para multipart/form-data o x-www-form-urlencoded
        return request.POST

    @transaction.atomic
    def _update_profile(self, user: CustomUserModel, request):
        data = self._get_request_data(request)
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
                return JsonResponse(
                    {'detail': 'El correo ya está en uso.'},
                    status=400,
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
            return JsonResponse(
                {'detail': e.message_dict},
                status=400,
            )

        user.save()
        loggin_event("Perfil actualizado correctamente")

        return JsonResponse(
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
            status=200,
        )

    @transaction.atomic
    def _change_password(self, user: CustomUserModel, data):
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')

        if not all([current_password, new_password, confirm_password]):
            loggin_event("Campos de contraseña incompletos")
            return JsonResponse(
                {'detail': 'Todos los campos de contraseña son obligatorios.'},
                status=400,
            )

        if not user.check_password(current_password):
            loggin_event("Contraseña actual incorrecta")
            return JsonResponse(
                {'detail': 'La contraseña actual es incorrecta.'},
                status=400,
            )

        if new_password != confirm_password:
            loggin_event("No coinciden las nuevas contraseñas")
            return JsonResponse(
                {'detail': 'Las contraseñas no coinciden.'},
                status=400,
            )

        if len(new_password) < 8:
            loggin_event("Nueva contraseña menor a 8 caracteres")
            return JsonResponse(
                {
                    'detail': (
                        'La nueva contraseña debe tener al menos '
                        '8 caracteres.'
                    )
                },
                status=400,
            )

        user.set_password(new_password)
        user.save()
        loggin_event("Contraseña actualizada correctamente")

        return JsonResponse(
            {'detail': 'Contraseña actualizada correctamente.'},
            status=200,
        )

    # ===================== ADMIN ACTIONS ===================== #
    def _ensure_admin(self, user: CustomUserModel):
        if getattr(user, 'roles', '') != 'ADMINISTRADOR':
            loggin_event("Intento no autorizado de acción admin")
            return JsonResponse(
                {'detail': 'No autorizado.'},
                status=403,
            )
        return None

    @transaction.atomic
    def _admin_toggle_active(self, admin: CustomUserModel, data):
        err = self._ensure_admin(admin)
        if err:
            return err
        target_id = data.get('target_user_id')
        if not target_id:
            return JsonResponse(
                {'detail': 'target_user_id es requerido.'},
                status=400,
            )
        try:
            target = CustomUserModel.objects.get(pk=target_id)
        except CustomUserModel.DoesNotExist:
            return JsonResponse(
                {'detail': 'Usuario objetivo no existe.'},
                status=404,
            )
        # Evitar que un admin se desactive a sí mismo accidentalmente
        if target.pk == admin.pk:
            return JsonResponse(
                {'detail': 'No puede cambiar su propio estado activo.'},
                status=400,
            )
        target.is_active = not target.is_active
        target.save()
        loggin_event(
            f"Admin {admin.email} cambió estado activo de {target.email} "
            f"a {target.is_active}"
        )
        return JsonResponse(
            {
                'detail': 'Estado actualizado',
                'user_id': target.pk,
                'is_active': target.is_active,
            },
            status=200,
        )

    @transaction.atomic
    def _admin_reset_password(self, admin: CustomUserModel, data):
        err = self._ensure_admin(admin)
        if err:
            return err
        target_id = data.get('target_user_id')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        if not all([target_id, new_password, confirm_password]):
            return JsonResponse(
                {
                    'detail': (
                        'Campos requeridos: target_user_id, new_password, '
                        'confirm_password.'
                    )
                },
                status=400,
            )
        if new_password != confirm_password:
            return JsonResponse(
                {'detail': 'Las contraseñas no coinciden.'},
                status=400,
            )
        if len(new_password) < 8:
            return JsonResponse(
                {'detail': 'La contraseña debe tener al menos 8 caracteres.'},
                status=400,
            )
        try:
            target = CustomUserModel.objects.get(pk=target_id)
        except CustomUserModel.DoesNotExist:
            return JsonResponse(
                {'detail': 'Usuario objetivo no existe.'},
                status=404,
            )
        # Un admin puede resetear su propia contraseña, eso sí está permitido
        target.set_password(new_password)
        target.save()
        loggin_event(
            f"Admin {admin.email} reseteó contraseña de usuario {target.email}"
        )
        return JsonResponse(
            {
                'detail': 'Contraseña reseteada correctamente.',
                'user_id': target.pk,
            },
            status=200,
        )

    @transaction.atomic
    def _update_license(self, user: CustomUserModel, data):
        """
        Crea o actualiza la licencia asociada al usuario actual.
        Espera campos: license_key (obligatorio), enterprise, url_server
        """
        license_key = (data.get('license_key') or '').strip()
        enterprise = (data.get('enterprise') or '').strip()
        url_server = (data.get('url_server') or '').strip()

        if not license_key:
            return JsonResponse(
                {'detail': 'La clave de licencia es obligatoria.'},
                status=400,
            )

        # Buscar la licencia activa o la más reciente del usuario
        lic = (
            License.objects.filter(user=user, is_active=True)
            .order_by('-activated_on', '-created_at')
            .first()
        )
        if not lic:
            lic = (
                License.objects.filter(user=user)
                .order_by('-activated_on', '-created_at')
                .first()
            )

        # Crear si no existe
        if not lic:
            lic = License(user=user)

        # Actualizar campos básicos
        lic.license_key = license_key
        if enterprise:
            lic.enterprise = enterprise
        if url_server:
            lic.url_server = url_server

        # Activar la licencia si el modelo lo soporta
        if hasattr(lic, 'is_active'):
            lic.is_active = True

        lic.save()

        def to_iso(dt):
            return dt.isoformat() if dt else None

        license_json = {
            'id': lic.id,
            'license_key': lic.license_key,
            'activated_on': to_iso(getattr(lic, 'activated_on', None)),
            'expires_on': to_iso(getattr(lic, 'expires_on', None)),
            'enterprise': getattr(lic, 'enterprise', None),
            'url_server': getattr(lic, 'url_server', None),
            'is_active': getattr(lic, 'is_active', None),
            'notes': getattr(lic, 'notes', None),
            'created_at': to_iso(getattr(lic, 'created_at', None)),
            'updated_at': to_iso(getattr(lic, 'updated_at', None)),
        }

        return JsonResponse({'license': license_json}, status=200)
