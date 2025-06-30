from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from products.models import Product, StockDay, StockDetail, BoxItems


class BoxItemsInlineAdmin(admin.TabularInline):
    model = BoxItems
    fields = (
        'product',
        'length',
        'qty_stem_flower',
        'stem_cost_price',
        'profit_margin',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class ProductAdmin(SimpleHistoryAdmin):
    list_display = (
        'name',
        'variety',
        'default_profit_margin',
        'is_active'
    )

    search_fields = (
        'name',
        'variety',
    )
    list_filter = (
        'is_active',
        'variety'
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
        ('Información del Producto', {
            'fields': (
                'name',
                'variety',
                'default_profit_margin'
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


class BoxItemsAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'stock_detail',
        'product',
        'length',
        'qty_stem_flower',
        'stem_cost_price',
        'profit_margin',
        'is_active'
    )

    search_fields = (
        'stock_detail__stock_day__date',
        'product__name',
    )
    list_filter = (
        'is_active',
        'product',
        'length'
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
                'stock_detail',
                'product',
                'length',
                'qty_stem_flower',
                'stem_cost_price',
                'profit_margin'
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


class StockDetailInlineAdmin(admin.TabularInline):
    model = StockDetail
    fields = (
        'partner',
        'tot_stem_flower',
        'tot_cost_price_box',
        'notes',
        'is_active'
    )
    readonly_fields = ('created_at', 'updated_at')
    extra = 0


class StockAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'date',
        'is_active'
    )
    list_filter = (
        'is_active',
        'date'
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
        ('Información del Stock', {
            'fields': (
                'date',
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
    inlines = [StockDetailInlineAdmin]


class StockDetailAdmin(SimpleHistoryAdmin):
    list_display = (
        'id',
        'stock_day',
        'partner',
        'tot_stem_flower',
        'tot_cost_price_box',
        'is_active'
    )

    search_fields = (
        'stock_day__date',
        'product__name',
        'partner__name',
    )
    list_filter = (
        'is_active',
        'stock_day',
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
        ('Información del Detalle', {
            'fields': (
                'stock_day',
                'partner',
                'tot_stem_flower',
                'tot_cost_price_box'
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
    inlines = [BoxItemsInlineAdmin]


admin.site.register(Product, ProductAdmin)
admin.site.register(StockDay, StockAdmin)
admin.site.register(StockDetail, StockDetailAdmin)
admin.site.register(BoxItems, BoxItemsAdmin)
