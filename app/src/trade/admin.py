from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from trade.models import Order, OrderItems, Invoice, InvoiceItems, CreditNote, Payment, OrderBoxItems


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


class OrderItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'order',
        'id_stock_detail',
        'tot_stem_flower',
        'line_price',
        'is_active',
    )

    search_fields = (
        'order__id',
    )
    inlines = [OrderBoxItemsAdmin]


class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'order',
        'partner',
        'num_invoice',
        'type_document',
        'date',
        'due_date',
        'status'
    )
    search_fields = (
        'num_invoice',
        'type_document',
        'partner__name'
    )


class InvoiceItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'invoice',
        'tot_stem_flower',
        'line_price',
        'line_margin',
        'line_total'
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
