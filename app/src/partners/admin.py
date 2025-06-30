from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from partners.models import Partner, Contact, DAE, Bank


class ContactInlineAdmin(admin.TabularInline):
    model = Contact
    fields = (
        'name',
        'position',
        'phone',
        'email',
        'is_principal',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class BankInlineAdmin(admin.TabularInline):
    model = Bank
    fields = (
        'owner',
        'account_number',
        'bank_name',
        'swift_code',
        'iban',
        'national_bank',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class DAEInlineAdmin(admin.TabularInline):
    model = DAE
    fields = (
        'dae',
        'date_begin',
        'date_end',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class PartnerAdmin(SimpleHistoryAdmin):
    list_display = (
        'business_tax_id',
        'name',
        'short_name',
        'type_partner',
        'country',
        'city',
        'credit_term',
        'status',
        'is_verified',
        'is_active'
    )
    search_fields = (
        'business_tax_id',
        'name',
        'email',
        'short_name',
        'phone'
    )
    list_filter = (
        'type_partner',
        'country',
        'city',
        'status',
        'is_active',
        'is_verified',
        'consolidate',
        'credit_term'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated',
        'user_creator'
    )
    fieldsets = (
        ('Información Básica', {
            'fields': (
                'business_tax_id',
                'name',
                'short_name',
                'type_partner',
                'email',
                'phone'
            )
        }),
        ('Dirección', {
            'fields': (
                'address',
                'country',
                'city',
                'zip_code',
                'area_code',
                'dispatch_address'
            )
        }),
        ('Información Comercial', {
            'fields': (
                'credit_term',
                'default_profit_margin',
                'is_profit_margin_included',
                'consolidate',
                'cargo_reference',
                'dispatch_days'
            )
        }),
        ('Contacto Adicional', {
            'classes': ('collapse',),
            'fields': (
                'website',
                'skype',
                'email_payment',
                'seller'
            )
        }),
        ('Referencias Comerciales', {
            'classes': ('collapse',),
            'fields': (
                'reference_1',
                'contact_reference_1',
                'phone_reference_1',
                'reference_2',
                'contact_reference_2',
                'phone_reference_2'
            )
        }),
        ('Estado y Verificación', {
            'classes': ('collapse',),
            'fields': (
                'status',
                'date_aproved',
                'is_verified',
                'businnes_start'
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
    inlines = [ContactInlineAdmin, BankInlineAdmin, DAEInlineAdmin]


class ContactAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'position',
        'phone',
        'email',
        'is_principal',
        'partner',
        'is_active'
    )
    search_fields = (
        'name',
        'email',
        'partner__name',
        'phone'
    )
    list_filter = (
        'is_principal',
        'is_active',
        'partner'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated'
    )
    fieldsets = (
        ('Información del Contacto', {
            'fields': (
                'partner',
                'name',
                'position',
                'phone',
                'email',
                'is_principal'
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


class BankAdmin(SimpleHistoryAdmin):
    list_display = (
        'owner',
        'partner',
        'account_number',
        'bank_name',
        'swift_code',
        'iban',
        'national_bank',
        'is_active'
    )

    search_fields = (
        'partner__name',
        'account_number',
        'bank_name',
        'swift_code'
    )
    list_filter = (
        'national_bank',
        'is_active',
        'partner'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated'
    )
    fieldsets = (
        ('Información Bancaria', {
            'fields': (
                'partner',
                'owner',
                'account_number',
                'bank_name',
                'swift_code',
                'iban',
                'national_bank'
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


class DAEAdmin(SimpleHistoryAdmin):
    list_display = (
        'partner',
        'dae',
        'date_begin',
        'date_end',
        'is_active'
    )

    search_fields = (
        'dae',
        'partner__name'
    )
    list_filter = (
        'is_active',
        'date_begin',
        'date_end'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'id_user_created',
        'id_user_updated'
    )
    fieldsets = (
        ('Información DAE', {
            'fields': (
                'partner',
                'dae',
                'date_begin',
                'date_end'
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


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(DAE, DAEAdmin)
