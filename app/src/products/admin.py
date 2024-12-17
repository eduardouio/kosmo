from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from products.models import Product, StockDay, StockDetail


class ProductAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'variety',
        'default_profit_margin',
    )

    search_fields = (
        'name',
        'variety',
    )


class StockAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
    )


class StockDetailAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'stock_day',
        'partner',
        'tot_stem_flower',
        'stem_cost_price_box',
    )

    search_fields = (
        'stock_day__date',
        'product__name',
        'partner__name',
    )


admin.site.register(Product, ProductAdmin)
admin.site.register(StockDay, StockAdmin)
admin.site.register(StockDetail, StockDetailAdmin)
