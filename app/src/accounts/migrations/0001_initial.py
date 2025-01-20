# Generated by Django 4.2.14 on 2025-01-17 16:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUserModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='correo electrónico')),
                ('picture', models.ImageField(blank=True, help_text='Imagen de perfil del usuario.', upload_to='accounts/pictures', verbose_name='imagen de perfil')),
                ('is_confirmed_mail', models.BooleanField(default=False, help_text='Estado de confirmación del correo electrónico.', verbose_name='correo electrónico confirmado')),
                ('notes', models.TextField(blank=True, verbose_name='notas')),
                ('roles', models.CharField(choices=[('ADMINISTRADOR', 'ADMINISTRADOR'), ('VENTAS', 'VENTAS')], default='ADMINISTRADOR', max_length=20, verbose_name='Role')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('license_key', models.CharField(max_length=250, unique=True, verbose_name='clave de licencia')),
                ('activated_on', models.DateTimeField(blank=True, null=True, verbose_name='activada el')),
                ('expires_on', models.DateTimeField(blank=True, null=True, verbose_name='expira el')),
                ('enterprise', models.CharField(default='KOSMOFLOWERS', max_length=50, verbose_name='Empresa')),
                ('is_active', models.BooleanField(default=False, verbose_name='Activo?')),
                ('url_server', models.URLField(blank=True, null=True, verbose_name='URL del servidor')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HistoricalLicense',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('license_key', models.CharField(db_index=True, max_length=250, verbose_name='clave de licencia')),
                ('activated_on', models.DateTimeField(blank=True, null=True, verbose_name='activada el')),
                ('expires_on', models.DateTimeField(blank=True, null=True, verbose_name='expira el')),
                ('enterprise', models.CharField(default='KOSMOFLOWERS', max_length=50, verbose_name='Empresa')),
                ('is_active', models.BooleanField(default=False, verbose_name='Activo?')),
                ('url_server', models.URLField(blank=True, null=True, verbose_name='URL del servidor')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical license',
                'verbose_name_plural': 'historical licenses',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
