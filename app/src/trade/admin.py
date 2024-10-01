from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from trade.models import Order, OrderItems, Invoice, InvoiceItems, CreditNote, Payment


class OrderAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'partner',
        'date',
        'status',
        'total_price',
        'discount',
        'qb_total',
        'hb_total'
    )
    search_fields = (
        'id',
        'date',
        'partner__name',
        'status'
    )


class OrderItemsAdmin(SimpleHistoryAdmin):
    pass


class InvoiceAdmin(SimpleHistoryAdmin):
    pass


class InvoiceItemsAdmin(SimpleHistoryAdmin):
    pass


class CreditNoteAdmin(SimpleHistoryAdmin):
    pass


class PaymentAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems, OrderItemsAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItems, InvoiceItemsAdmin)
admin.site.register(CreditNote, CreditNoteAdmin)
admin.site.register(Payment, PaymentAdmin)
