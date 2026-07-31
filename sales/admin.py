from django.contrib import admin
from .models import Booking, Tempo

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_name', 'model', 'qty', 'amount', 'status', 'channel', 'date')
    list_filter = ('status', 'channel', 'date')
    search_fields = ('booking_id', 'customer_name', 'mobile')
    readonly_fields = ('booking_id', 'date')   # amount is editable in admin

@admin.register(Tempo)
class TempoAdmin(admin.ModelAdmin):
    list_display = ('tempo_id', 'vehicle_number', 'place', 'items', 'status')
    list_filter = ('status',)
    search_fields = ('tempo_id', 'vehicle_number')