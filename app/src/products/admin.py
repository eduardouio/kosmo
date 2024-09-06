from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from products.models import Product, StockDay, StockDetail


class ProductAdmin(SimpleHistoryAdmin):
    pass


class StockAdmin(SimpleHistoryAdmin):
    pass


class StockDetailAdmin(SimpleHistoryAdmin):
    pass


admin.site.register(Product, ProductAdmin)
admin.site.register(StockDay, StockAdmin)
admin.site.register(StockDetail, StockDetailAdmin)
