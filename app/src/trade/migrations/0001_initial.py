# Generated by Django 4.2.14 on 2025-03-11 23:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('partners', '0001_initial'),
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('num_invoice', models.PositiveIntegerField(verbose_name='Numero de Factura')),
                ('type_document', models.CharField(choices=[('FAC_VENTA', 'FACTURA VENTA'), ('FAC_COMPRA', 'FACTURA COMPRA')], max_length=50, verbose_name='Tipo de Documento')),
                ('type_invoice', models.CharField(choices=[('EXPORT', 'EXPORTACIÓN'), ('INTERN', 'NACIONAL'), ('NA', 'NO APLICA')], max_length=50, verbose_name='Tipo de Factura')),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Fecha')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio total')),
                ('qb_total', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total QB')),
                ('hb_total', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total HB')),
                ('awb', models.CharField(blank=True, max_length=50, null=True, verbose_name='MAWB')),
                ('dae_export', models.CharField(blank=True, max_length=50, null=True, verbose_name='DAE Exportación')),
                ('hawb', models.CharField(blank=True, max_length=50, null=True, verbose_name='HAWB')),
                ('cargo_agency', models.CharField(blank=True, max_length=50, null=True, verbose_name='Agencia de Carga')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Fecha de entrega')),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Peso KG')),
                ('status', models.CharField(choices=[('PENDIENTE', 'PENDIENTE'), ('PAGADO', 'PAGADO'), ('ANULADO', 'ANULADO')], default='PENDIENTE', max_length=50, verbose_name='Estado')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(auto_now=True, verbose_name='Fecha')),
                ('type_document', models.CharField(choices=[('ORD_VENTA', 'ORDEN DE VENTA'), ('ORD_COMPRA', 'ORDEN DE COMPRA')], max_length=50, verbose_name='Tipo de Documento')),
                ('num_order', models.CharField(blank=True, max_length=50, null=True, verbose_name='PO Socio')),
                ('delivery_date', models.DateField(blank=True, default=None, null=True, verbose_name='Fecha de entrega')),
                ('status', models.CharField(choices=[('PENDIENTE', 'PENDIENTE'), ('CONFIRMADO', 'CONFIRMADO'), ('MODIFICADO', 'MODIFICADO'), ('FACTURADO', 'FACTURADO'), ('CANCELADO', 'CANCELADO')], max_length=50)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Descuento')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio total')),
                ('qb_total', models.PositiveSmallIntegerField(default=0, verbose_name='Total QB')),
                ('hb_total', models.PositiveSmallIntegerField(default=0, verbose_name='Total QB')),
                ('total_stem_flower', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total Tallos')),
                ('parent_order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='trade.order')),
                ('partner', models.ForeignKey(help_text='C customer S supplier', on_delete=django.db.models.deletion.CASCADE, to='partners.partner')),
                ('stock_day', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.stockday')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateField(verbose_name='Fecha de pago')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('method', models.CharField(default='OTRO', max_length=50, verbose_name='Metodo de pago')),
                ('bank', models.CharField(blank=True, max_length=50, null=True, verbose_name='Banco')),
                ('nro_account', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nro de Cuenta')),
                ('nro_operation', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nro de Operación')),
                ('invoices', models.ManyToManyField(to='trade.invoice')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('id_stock_detail', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Detalle de Stock')),
                ('line_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Precio Linea')),
                ('line_margin', models.DecimalField(decimal_places=2, default=0.06, max_digits=5, verbose_name='Margen Linea')),
                ('line_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Precio Total')),
                ('tot_stem_flower', models.IntegerField(default=0, help_text='Cantidad de tallos de flor', verbose_name='Unds Tallos')),
                ('box_model', models.CharField(choices=[('HB', 'HB'), ('QB', 'QB'), ('FB', 'FB')], max_length=50, verbose_name='Tipo de caja')),
                ('quantity', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Cant Cajas')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('is_modified', models.BooleanField(default=False, verbose_name='Modificado')),
                ('parent_order_item', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Item de orden padre')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.order')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrderBoxItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('length', models.PositiveSmallIntegerField(verbose_name='Largo CM')),
                ('qty_stem_flower', models.IntegerField(default=0, help_text='Cantidad de tallos de flor', verbose_name='Cant Tallos')),
                ('stem_cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio de costo Tallo')),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0.06, max_digits=5, verbose_name='Margen de Ganancia')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.orderitems')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InvoiceItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('qty_stem_flower', models.IntegerField(default=0, verbose_name='Cantidad Tallos')),
                ('line_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('line_discount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Descuento')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.invoice')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.orderitems')),
            ],
            options={
                'get_latest_by': 'created_at',
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='invoice',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.order'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='partner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='partners.partner'),
        ),
        migrations.CreateModel(
            name='HistoricalPayment',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('date', models.DateField(verbose_name='Fecha de pago')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('method', models.CharField(default='OTRO', max_length=50, verbose_name='Metodo de pago')),
                ('bank', models.CharField(blank=True, max_length=50, null=True, verbose_name='Banco')),
                ('nro_account', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nro de Cuenta')),
                ('nro_operation', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nro de Operación')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical payment',
                'verbose_name_plural': 'historical payments',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrderItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('id_stock_detail', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Detalle de Stock')),
                ('line_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Precio Linea')),
                ('line_margin', models.DecimalField(decimal_places=2, default=0.06, max_digits=5, verbose_name='Margen Linea')),
                ('line_total', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Precio Total')),
                ('tot_stem_flower', models.IntegerField(default=0, help_text='Cantidad de tallos de flor', verbose_name='Unds Tallos')),
                ('box_model', models.CharField(choices=[('HB', 'HB'), ('QB', 'QB'), ('FB', 'FB')], max_length=50, verbose_name='Tipo de caja')),
                ('quantity', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Cant Cajas')),
                ('is_deleted', models.BooleanField(default=False, verbose_name='Eliminado')),
                ('is_modified', models.BooleanField(default=False, verbose_name='Modificado')),
                ('parent_order_item', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Item de orden padre')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.order')),
            ],
            options={
                'verbose_name': 'historical order items',
                'verbose_name_plural': 'historical order itemss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrderBoxItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('length', models.PositiveSmallIntegerField(verbose_name='Largo CM')),
                ('qty_stem_flower', models.IntegerField(default=0, help_text='Cantidad de tallos de flor', verbose_name='Cant Tallos')),
                ('stem_cost_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio de costo Tallo')),
                ('profit_margin', models.DecimalField(decimal_places=2, default=0.06, max_digits=5, verbose_name='Margen de Ganancia')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order_item', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.orderitems')),
                ('product', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='products.product')),
            ],
            options={
                'verbose_name': 'historical order box items',
                'verbose_name_plural': 'historical order box itemss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha')),
                ('type_document', models.CharField(choices=[('ORD_VENTA', 'ORDEN DE VENTA'), ('ORD_COMPRA', 'ORDEN DE COMPRA')], max_length=50, verbose_name='Tipo de Documento')),
                ('num_order', models.CharField(blank=True, max_length=50, null=True, verbose_name='PO Socio')),
                ('delivery_date', models.DateField(blank=True, default=None, null=True, verbose_name='Fecha de entrega')),
                ('status', models.CharField(choices=[('PENDIENTE', 'PENDIENTE'), ('CONFIRMADO', 'CONFIRMADO'), ('MODIFICADO', 'MODIFICADO'), ('FACTURADO', 'FACTURADO'), ('CANCELADO', 'CANCELADO')], max_length=50)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Descuento')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio total')),
                ('qb_total', models.PositiveSmallIntegerField(default=0, verbose_name='Total QB')),
                ('hb_total', models.PositiveSmallIntegerField(default=0, verbose_name='Total QB')),
                ('total_stem_flower', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total Tallos')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('parent_order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.order')),
                ('partner', models.ForeignKey(blank=True, db_constraint=False, help_text='C customer S supplier', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='partners.partner')),
                ('stock_day', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='products.stockday')),
            ],
            options={
                'verbose_name': 'historical order',
                'verbose_name_plural': 'historical orders',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalInvoiceItems',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('qty_stem_flower', models.IntegerField(default=0, verbose_name='Cantidad Tallos')),
                ('line_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Precio')),
                ('line_discount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Descuento')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('invoice', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.invoice')),
                ('order_item', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.orderitems')),
            ],
            options={
                'verbose_name': 'historical invoice items',
                'verbose_name_plural': 'historical invoice itemss',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalInvoice',
            fields=[
                ('notes', models.TextField(blank=True, default=None, help_text='Notas del registro.', null=True, verbose_name='notas')),
                ('created_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de creación del registro.', verbose_name='fecha de creación')),
                ('updated_at', models.DateTimeField(blank=True, editable=False, help_text='Fecha de ultima actualización del registro.', verbose_name='fecha de actualización')),
                ('is_active', models.BooleanField(default=True, help_text='Estado del registro.', verbose_name='activo')),
                ('id_user_created', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario creador del registro 0 es anonimo.', null=True, verbose_name='usuario creador')),
                ('id_user_updated', models.PositiveIntegerField(blank=True, default=0, help_text='Identificador del usuario actualizador del registro.', null=True, verbose_name='usuario actualizador')),
                ('id', models.IntegerField(blank=True, db_index=True)),
                ('num_invoice', models.PositiveIntegerField(verbose_name='Numero de Factura')),
                ('type_document', models.CharField(choices=[('FAC_VENTA', 'FACTURA VENTA'), ('FAC_COMPRA', 'FACTURA COMPRA')], max_length=50, verbose_name='Tipo de Documento')),
                ('type_invoice', models.CharField(choices=[('EXPORT', 'EXPORTACIÓN'), ('INTERN', 'NACIONAL'), ('NA', 'NO APLICA')], max_length=50, verbose_name='Tipo de Factura')),
                ('date', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de vencimiento')),
                ('total_price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Precio total')),
                ('qb_total', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total QB')),
                ('hb_total', models.PositiveSmallIntegerField(blank=True, default=0, null=True, verbose_name='Total HB')),
                ('awb', models.CharField(blank=True, max_length=50, null=True, verbose_name='MAWB')),
                ('dae_export', models.CharField(blank=True, max_length=50, null=True, verbose_name='DAE Exportación')),
                ('hawb', models.CharField(blank=True, max_length=50, null=True, verbose_name='HAWB')),
                ('cargo_agency', models.CharField(blank=True, max_length=50, null=True, verbose_name='Agencia de Carga')),
                ('delivery_date', models.DateField(blank=True, null=True, verbose_name='Fecha de entrega')),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Peso KG')),
                ('status', models.CharField(choices=[('PENDIENTE', 'PENDIENTE'), ('PAGADO', 'PAGADO'), ('ANULADO', 'ANULADO')], default='PENDIENTE', max_length=50, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='trade.order')),
                ('partner', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='partners.partner')),
            ],
            options={
                'verbose_name': 'historical invoice',
                'verbose_name_plural': 'historical invoices',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='CreditNote',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('num_credit_note', models.CharField(max_length=50, verbose_name='Numero de nota de crédito')),
                ('date', models.DateField(verbose_name='Fecha de la nota de crédito')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Monto')),
                ('reason', models.TextField(verbose_name='Motivo de la nota de crédito')),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trade.invoice')),
            ],
        ),
    ]
