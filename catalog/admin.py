from django.contrib import admin
from .models import Model

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'size', 'available', 'selling_price')
    list_filter = ('category',)
    search_fields = ('sku', 'name')
    readonly_fields = ('wholesale_sold', 'retail_sold')