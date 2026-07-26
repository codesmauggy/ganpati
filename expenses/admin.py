from django.contrib import admin
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_id', 'date', 'category', 'description', 'amount', 'paid_by')
    list_filter = ('category', 'date')
    search_fields = ('expense_id', 'description')
    readonly_fields = ('expense_id', 'date')