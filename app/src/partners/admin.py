from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from partners.models import Partner, Contact, DAE


class PartnerAdmin(SimpleHistoryAdmin):
    list_display =(
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
        'email'
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
        'partner__name'
    )


class DAEAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(DAE, DAEAdmin)
