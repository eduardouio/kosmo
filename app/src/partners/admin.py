from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from partners.models import Partner, Contact, DAE


class PartnerAdmin(SimpleHistoryAdmin):
    pass


class ContactAdmin(SimpleHistoryAdmin):
    pass


class DAEAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Partner, PartnerAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(DAE, DAEAdmin)
