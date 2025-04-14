from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from partners.models import Partner, Contact, DAE, Bank


class PartnerAdmin(SimpleHistoryAdmin):
    list_display = (
        'business_tax_id',
        'name',
        'type_partner',
        'address',
        'country',
        'city',
        'credit_term',
        'email'
    )
    search_fields = (
        'business_tax_id',
        'name',
        'email',
        'short_name',
        'phone'
    )


class ContactAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'position',
        'phone',
        'email',
        'is_principal',
        'partner'
    )
    search_fields = (
        'name',
        'email',
        'partner__name',
        'phone'
    )


class BankAdmin(SimpleHistoryAdmin):
    list_display = (
        'owner',
        'partner',
        'account_number',
        'bank_name',
        'swift_code',
        'iban',
        'national_bank'
    )

    search_fields = (
        'partner__name',
        'account_number',
        'bank_name',
        'swift_code'
    )


class DAEAdmin(SimpleHistoryAdmin):
    list_display = (
        'partner',
        'dae',
        'date_begin',
        'date_end'
    )

    search_fields = (
        'dae',
        'partner__name'
    )


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Bank, BankAdmin)
admin.site.register(DAE, DAEAdmin)
