from django.contrib import admin
from .models import Worker

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('worker_id', 'name', 'role', 'category', 'attendance', 'today_production', 'pending_salary')
    list_filter = ('category', 'attendance')
    search_fields = ('worker_id', 'name')
    readonly_fields = ('worker_id',)