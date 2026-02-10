from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Candle, Category, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'name_ru', 'order')
    search_fields = ('name', 'name_ru')
    fieldsets = (
        (None, {'fields': ('name', 'name_ru', 'description', 'order')}),
    )
    def display_name(self, obj):
        return obj.display_name()
    display_name.short_description = _('Название')

@admin.register(Candle)
class CandleAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'price', 'category', 'order', 'is_hit', 'is_on_sale', 'discount_percent')
    #list_editable = ('price', 'category', 'order', 'is_hit', 'is_on_sale', 'discount_percent')
    list_filter = ('is_hit', 'is_on_sale', 'category')
    search_fields = ('name', 'name_ru', 'category__name')
    ordering = ('order', '-id')
    fieldsets = (
        (None, {
            'fields': ('name', 'name_ru', 'description', 'description_ru')
        }),
        ('Catalog', {
            'fields': ('price', 'image', 'category', 'order', 'is_hit', 'is_on_sale', 'discount_percent')
        }),
    )
    def display_name(self, obj):
        return obj.display_name()
    display_name.short_description = _('Название')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'quantity')
    fields = ('candle', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'phone', 'city', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'city')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Контактні дані', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('city', 'warehouse')
        }),
        ('Інші дані', {
            'fields': ('payment_method', 'notes', 'agree_to_terms', 'status')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

