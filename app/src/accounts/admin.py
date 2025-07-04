from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import CustomUserModel
from accounts.forms import CustomCreationForm, CustomChangeForm


class CustomUserModelAdmin(UserAdmin):
    add_form = CustomCreationForm
    form = CustomChangeForm

    model = CustomUserModel

    fieldsets = (
        ('Básico', {
            'fields': (
                'email', 'password', 'is_active',
            )
        }),
        ('Información Personal', {
            'fields': (
                'first_name', 'last_name', 'phone'
            )
        }),
        ('Permisos', {
            'fields': (
                'is_staff', 'is_superuser', 'groups', 'user_permissions'
            )
        }),
        ('Información del Sistema', {
            'classes': ('collapse',),
            'fields': (
                'is_confirmed_mail',
                'date_joined',
                'last_login'
            )
        })
    )
    add_fieldsets = (
        ('Básico', {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2',
                'is_staff', 'is_active'
            )
        }),
    )

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_confirmed_mail',
        'is_staff',
        'is_superuser',
        'date_joined'
    )

    list_filter = (
        'is_active',
        'is_confirmed_mail',
        'is_staff',
        'is_superuser',
        'date_joined'
    )

    search_fields = ('email', 'first_name', 'last_name', 'phone')

    readonly_fields = ('date_joined', 'last_login')

    ordering = ('-date_joined',)


admin.site.register(CustomUserModel, CustomUserModelAdmin)