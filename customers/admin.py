from django.contrib import admin
from .models import Customer, CustomerPayment, LedgerEntry

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'name', 'contact', 'tag', 'is_active', 'created_at')
    list_filter = ('tag', 'is_active')
    search_fields = ('customer_id', 'name', 'contact')
    readonly_fields = ('customer_id', 'created_at')

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'customer', 'amount', 'mode', 'date', 'received_by')
    list_filter = ('mode', 'date')
    search_fields = ('payment_id', 'reference')
    readonly_fields = ('payment_id', 'date')

@admin.register(LedgerEntry)
class LedgerEntryAdmin(admin.ModelAdmin):
    list_display = ('customer', 'date', 'type', 'reference', 'debit', 'credit')
    list_filter = ('type', 'date')
    search_fields = ('reference',)