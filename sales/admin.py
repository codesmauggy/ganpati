from django.contrib import admin
from django import forms
from .models import Booking, RetailBooking, WholesaleBooking, OrderItem, Tempo


# ---- Custom form for RetailBooking ----
class RetailBookingForm(forms.ModelForm):
    class Meta:
        model = RetailBooking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].required = False
        self.fields['mobile'].required = False
        self.fields['village'].required = False

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        customer_name = cleaned_data.get('customer_name')
        mobile = cleaned_data.get('mobile')

        if customer:
            if not customer_name:
                cleaned_data['customer_name'] = customer.name
            if not mobile:
                cleaned_data['mobile'] = customer.contact
            if not cleaned_data.get('village'):
                cleaned_data['village'] = customer.village or ''
        else:
            if not customer_name or not mobile:
                raise forms.ValidationError(
                    'Either select a customer OR provide both Customer name and Mobile.'
                )
        return cleaned_data


# ---- Custom form for WholesaleBooking ----
class WholesaleBookingForm(forms.ModelForm):
    class Meta:
        model = WholesaleBooking
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer_name'].required = False
        self.fields['mobile'].required = False
        self.fields['village'].required = False

    def clean(self):
        cleaned_data = super().clean()
        customer = cleaned_data.get('customer')
        customer_name = cleaned_data.get('customer_name')
        mobile = cleaned_data.get('mobile')

        if customer:
            if not customer_name:
                cleaned_data['customer_name'] = customer.name
            if not mobile:
                cleaned_data['mobile'] = customer.contact
            if not cleaned_data.get('village'):
                cleaned_data['village'] = customer.village or ''
        else:
            if not customer_name or not mobile:
                raise forms.ValidationError(
                    'Either select a customer OR provide both Customer name and Mobile.'
                )
        return cleaned_data


# ---- Inline for OrderItem ----
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    autocomplete_fields = ('model',)
    readonly_fields = ('line_total',)   # shows computed total
    fields = ('model', 'qty', 'unit_price', 'line_total')


# ---- Register base Booking for autocomplete support ----
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    search_fields = ('booking_id', 'customer_name', 'mobile')
    list_display = ('booking_id', 'customer_name', 'status', 'date')


# ---- RetailBooking Admin ----
@admin.register(RetailBooking)
class RetailBookingAdmin(admin.ModelAdmin):
    form = RetailBookingForm
    list_display = ('booking_id', 'customer_name', 'model', 'qty', 'amount', 'advance', 'status', 'date')
    list_filter = ('status', 'date')
    search_fields = ('booking_id', 'customer_name', 'mobile')
    readonly_fields = ('booking_id', 'date')
    autocomplete_fields = ('customer', 'model')

    def save_model(self, request, obj, form, change):
        if obj.customer:
            obj.customer_name = obj.customer.name
            obj.mobile = obj.customer.contact
            if not obj.village:
                obj.village = obj.customer.village or ''
        super().save_model(request, obj, form, change)


# ---- WholesaleBooking Admin ----
@admin.register(WholesaleBooking)
class WholesaleBookingAdmin(admin.ModelAdmin):
    form = WholesaleBookingForm
    list_display = (
        'booking_id', 'customer_name', 'amount',  # amount is the total
        'total_qty', 'advance', 'status', 'date'
    )
    list_filter = ('status', 'date')
    search_fields = ('booking_id', 'customer_name', 'mobile')
    readonly_fields = ('booking_id', 'date', 'amount')   # amount read-only
    inlines = [OrderItemInline]
    autocomplete_fields = ('customer',)

    def total_qty(self, obj):
        return obj.total_qty
    total_qty.short_description = 'Total Qty'


# ---- Tempo Admin ----
@admin.register(Tempo)
class TempoAdmin(admin.ModelAdmin):
    list_display = ('tempo_id', 'vehicle_number', 'place', 'items', 'status')
    list_filter = ('status',)
    search_fields = ('tempo_id', 'vehicle_number')
    autocomplete_fields = ('bookings',)