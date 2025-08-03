from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from trade.models import (
    Order, OrderItems, Invoice, InvoiceItems,
    CreditNote, Payment, OrderBoxItems, InvoiceBoxItems
)
from trade.models.Payment import PaymentDetail


class OrderAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'serie',
        'consecutive',
        'partner',
        'date',
        'type_document',
        'status',
        'total_price',
        'discount',
        'qb_total',
        'hb_total',
        'is_active'
    )
    search_fields = (
        'id',
        'serie',
        'consecutive',
        'date',
        'partner__name',
        'status',
        'num_order',
        'num_invoice'
    )
    list_filter = (
        'type_document',
        'status',
        'is_active',
        'serie',
        'delivery_date',
        'is_invoiced'
    )
    readonly_fields = (
        'id',
        'date',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated',
        'user_creator'
    )
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'serie',
                'consecutive',
                'stock_day',
                'partner',
                'type_document',
                'parent_order',
                'num_order',
                'delivery_date',
                'status'
            )
        }),
        ('Fechas (Solo Lectura)', {
            'fields': (
                'date',
            )
        }),
        ('Totales y Precios', {
            'fields': (
                'total_price',
                'total_margin',
                'discount',
                'comision_seler',
                'total_bunches',
                'total_stem_flower'
            )
        }),
        ('Tipos de Cajas', {
            'fields': (
                'eb_total',
                'qb_total',
                'hb_total',
                'fb_total'
            )
        }),
        ('Información de Facturación', {
            'fields': (
                'is_invoiced',
                'id_invoice',
                'num_invoice'
            )
        }),
        ('Datos del Sistema', {
            'classes': ('collapse',),
            'fields': (
                'notes',
                'is_active',
                'created_at',
                'updated_at',
                'id_user_created',
                'id_user_updated'
            )
        })
    )


class OrderBoxItemsAdmin(admin.TabularInline):
    model = OrderBoxItems
    list_display = (
        'order_item',
        'product',
        'qty_stem_flower',
        'stem_cost_price',
        'profit_margin',
        'length'
    )
    fields = (
        'product',
        'qty_stem_flower',
        'stem_cost_price',
        'profit_margin',
        'length',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class OrderItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'order',
        'id_stock_detail',
        'tot_stem_flower',
        'line_price',
        'line_margin',
        'line_total',
        'box_model',
        'quantity',
        'is_active',
        'is_deleted',
        'is_modified'
    )

    search_fields = (
        'order__id',
        'id_stock_detail',
        'box_model'
    )
    list_filter = (
        'box_model',
        'is_active',
        'is_deleted',
        'is_modified',
        'order__type_document'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated',
        'eb_total',
        'qb_total',
        'hb_total',
        'fb_total'
    )
    fieldsets = (
        ('Información del Item', {
            'fields': (
                'order',
                'id_stock_detail',
                'box_model',
                'quantity',
                'tot_stem_flower',
                'total_bunches'
            )
        }),
        ('Precios y Márgenes', {
            'fields': (
                'line_price',
                'line_margin',
                'line_total',
                'line_commission'
            )
        }),
        ('Estado y Control', {
            'fields': (
                'is_deleted',
                'is_modified',
                'parent_order_item'
            )
        }),
        ('Totales por Tipo de Caja (Solo Lectura)', {
            'classes': ('collapse',),
            'fields': (
                'eb_total',
                'qb_total',
                'hb_total',
                'fb_total'
            )
        }),
        ('Datos del Sistema', {
            'classes': ('collapse',),
            'fields': (
                'notes',
                'is_active',
                'created_at',
                'updated_at',
                'id_user_created',
                'id_user_updated'
            )
        })
    )
    inlines = [OrderBoxItemsAdmin]


class InvoiceBoxItemsInlineAdmin(admin.TabularInline):
    model = InvoiceBoxItems
    fields = (
        'product',
        'length',
        'qty_stem_flower',
        'stem_cost_price',
        'profit_margin',
        'commission',
        'total_bunches',
        'stems_bunch',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class InvoiceItemsInlineAdmin(admin.TabularInline):
    model = InvoiceItems
    fields = (
        'id_order_item',
        'box_model',
        'quantity',
        'tot_stem_flower',
        'total_bunches',
        'line_price',
        'line_margin',
        'line_total',
        'line_commission',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'serie',
        'consecutive',
        'num_invoice',
        'order',
        'partner',
        'type_document',
        'date',
        'due_date',
        'status',
        'total_price',
        'total_margin',
        'is_active'
    )
    search_fields = (
        'id',
        'num_invoice',
        'serie',
        'consecutive',
        'type_document',
        'partner__name',
        'awb',
        'marking',
        'po_number',
        'hawb',
        'dae_export'
    )
    list_filter = (
        'type_document',
        'status',
        'serie',
        'is_active',
        'delivery_date'
    )
    readonly_fields = (
        'id',
        'date',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated',
        'user_creator',
        'total_invoice',
        'days_to_due',
        'is_dued',
        'days_overdue'
    )
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'serie',
                'consecutive',
                'marking',
                'order',
                'partner',
                'num_invoice',
                'type_document',
                'due_date',
                'status'
            )
        }),
        ('Fechas (Solo Lectura)', {
            'fields': (
                'date',
            )
        }),
        ('Información Comercial', {
            'fields': (
                'po_number',
                'delivery_date'
            )
        }),
        ('Información de Envío', {
            'fields': (
                'awb',
                'hawb',
                'dae_export',
                'cargo_agency',
                'weight'
            )
        }),
        ('Totales y Precios', {
            'fields': (
                'total_price',
                'total_margin',
                'comision_seler',
                'total_pieces',
                'tot_stem_flower',
                'total_bunches'
            )
        }),
        ('Tipos de Cajas', {
            'fields': (
                'eb_total',
                'qb_total',
                'hb_total',
                'fb_total'
            )
        }),
        ('Propiedades Calculadas (Solo Lectura)', {
            'classes': ('collapse',),
            'fields': (
                'total_invoice',
                'days_to_due',
                'is_dued',
                'days_overdue'
            )
        }),
        ('Datos del Sistema', {
            'classes': ('collapse',),
            'fields': (
                'notes',
                'is_active',
                'created_at',
                'updated_at',
                'id_user_created',
                'id_user_updated'
            )
        })
    )
    inlines = [InvoiceItemsInlineAdmin]


class InvoiceItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'invoice',
        'id_order_item',
        'box_model',
        'quantity',
        'tot_stem_flower',
        'total_bunches',
        'line_price',
        'line_margin',
        'line_total',
        'is_active'
    )
    search_fields = (
        'invoice__id',
        'invoice__num_invoice',
        'id_order_item',
        'box_model'
    )
    list_filter = (
        'box_model',
        'is_active',
        'invoice__type_document'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated'
    )
    fieldsets = (
        ('Información del Item', {
            'fields': (
                'invoice',
                'id_order_item',
                'box_model',
                'quantity',
                'tot_stem_flower',
                'total_bunches'
            )
        }),
        ('Precios y Márgenes', {
            'fields': (
                'line_price',
                'line_margin',
                'line_total',
                'line_commission'
            )
        }),
        ('Datos del Sistema', {
            'classes': ('collapse',),
            'fields': (
                'notes',
                'is_active',
                'created_at',
                'updated_at',
                'id_user_created',
                'id_user_updated'
            )
        })
    )
    inlines = [InvoiceBoxItemsInlineAdmin]


class PaymentDetailInline(admin.TabularInline):
    model = PaymentDetail
    fields = ('invoice', 'amount', 'is_active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')
    extra = 0
    verbose_name = "Factura Asociada"
    verbose_name_plural = "Facturas Asociadas"

    def get_queryset(self, request):
        """Incluir detalles de pago inactivos en admin"""
        return super().get_queryset(request).select_related('invoice')


class PaymentAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'payment_number',
        'date',
        'due_date',
        'type_transaction',
        'amount',
        'method',
        'status',
        'bank',
        'nro_operation',
        'processed_by',
        'approved_by',
        'is_active',
        'created_at'
    )
    search_fields = (
        'id',
        'payment_number',
        'nro_operation',
        'nro_account',
        'bank',
        'method',
        'status',
        'processed_by__username',
        'approved_by__username'
    )
    list_filter = (
        'type_transaction',
        'method',
        'status',
        'bank',
        'is_active',
        'date',
        'due_date',
        'approval_date',
        'processed_by',
        'approved_by'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated',
        'user_creator',
        'total_invoices_amount'
    )
    fieldsets = (
        ('Información Básica del Pago', {
            'fields': (
                'payment_number',
                'date',
                'due_date',
                'type_transaction',
                'amount',
                'status'
            )
        }),
        ('Información del Método de Pago', {
            'fields': (
                'method',
                'bank',
                'nro_account',
                'nro_operation',
                'document'
            )
        }),
        ('Información de Aprobación', {
            'fields': (
                'processed_by',
                'approved_by',
                'approval_date'
            )
        }),
        ('Totales Calculados (Solo Lectura)', {
            'classes': ('collapse',),
            'fields': (
                'total_invoices_amount',
            )
        }),
        ('Datos del Sistema (BaseModel)', {
            'classes': ('collapse',),
            'fields': (
                'notes',
                'is_active',
                'created_at',
                'updated_at',
                'id_user_created',
                'id_user_updated',
                'user_creator'
            )
        })
    )
    inlines = [PaymentDetailInline]
    actions = [
        'activate_payments', 'deactivate_payments', 'mark_as_confirmed',
        'convert_to_egreso', 'convert_to_ingreso'
    ]

    def get_queryset(self, request):
        """Sobrescribir queryset para incluir pagos inactivos en admin"""
        return self.model.objects.all()

    def total_invoices_amount(self, obj):
        """Mostrar el total de facturas asociadas"""
        return f"${obj.total_invoices_amount:,.2f}"
    total_invoices_amount.short_description = "Total Facturas"

    def activate_payments(self, request, queryset):
        """Acción para activar pagos seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} pago(s) activado(s).')
    activate_payments.short_description = "Activar pagos seleccionados"

    def deactivate_payments(self, request, queryset):
        """Acción para desactivar pagos seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} pago(s) desactivado(s).')
    deactivate_payments.short_description = "Desactivar pagos seleccionados"

    def mark_as_confirmed(self, request, queryset):
        """Acción para marcar pagos como confirmados"""
        updated = queryset.update(status='CONFIRMADO')
        self.message_user(request, f'{updated} pago(s) confirmado(s).')
    mark_as_confirmed.short_description = "Marcar como confirmados"

    def convert_to_egreso(self, request, queryset):
        """Acción para convertir pagos a EGRESO (pagos realizados)"""
        updated = queryset.update(type_transaction='EGRESO')
        self.message_user(request, f'{updated} pago(s) a EGRESO.')
    convert_to_egreso.short_description = "Convertir a EGRESO (Pagos)"

    def convert_to_ingreso(self, request, queryset):
        """Acción para convertir pagos a INGRESO (cobros recibidos)"""
        updated = queryset.update(type_transaction='INGRESO')
        self.message_user(request, f'{updated} pago(s) a INGRESO.')
    convert_to_ingreso.short_description = "Convertir a INGRESO (Cobros)"


class CreditNoteAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'num_credit_note',
        'invoice',
        'date',
        'amount',
        'reason'
    )
    list_filter = (
        'date',
        'invoice'
    )
    search_fields = (
        'num_credit_note',
        'invoice__num_invoice',
        'reason'
    )
    readonly_fields = (
        'id',
    )
    fieldsets = (
        ('Información de la Nota de Crédito', {
            'fields': (
                'num_credit_note',
                'invoice',
                'date',
                'amount',
                'reason'
            )
        }),
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems, OrderItemsAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItems, InvoiceItemsAdmin)
admin.site.register(CreditNote, CreditNoteAdmin)
admin.site.register(Payment, PaymentAdmin)
