from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from trade.models import Order, OrderItems, Invoice, InvoiceItems, CreditNote, Payment


class OrderAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'partner',
        'date',
        'type_document',
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
    list_display = (
        'id',
        'order',
        'id_stock_detail',
        'tot_stem_flower',
        'line_price',
    )


class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'order',
        'partner',
        'num_invoice',
        'type_document',
        'type_invoice',
        'date',
        'due_date',
        'status'
    )
    search_fields = (
        'num_invoice',
        'type_document',
        'type_invoice',
        'partner__name'
    )


class InvoiceItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'invoice',
        'order_item',
        'qty_stem_flower',
        'line_price',
        'line_discount'
    )


class PaymentAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'amount',
        'method',
        'nro_operation',
        'bank'
    )


class CreditNoteAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItems, OrderItemsAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceItems, InvoiceItemsAdmin)
admin.site.register(CreditNote, CreditNoteAdmin)
admin.site.register(Payment, PaymentAdmin)
