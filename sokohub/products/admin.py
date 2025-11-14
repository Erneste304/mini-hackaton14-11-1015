from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'vendor', 'price', 'stock', 'status', 'created_at')
    list_filter = ('status', 'vendor', 'created_at')
    search_fields = ('name', 'description', 'vendor__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('price', 'stock', 'status')
    list_per_page = 20

    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'name', 'description')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock', 'status')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )