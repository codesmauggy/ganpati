from rest_framework import serializers
from django.db import models
from .models import Customer, CustomerPayment, LedgerEntry
from sales.models import Booking
from sales.serializers import BookingSerializer

class CustomerSerializer(serializers.ModelSerializer):
    ref_by_display = serializers.CharField(source='ref_by.full_name', read_only=True)
    total_billed = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()
    last_transaction_date = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            'id', 'customer_id', 'name', 'contact', 'alt_contact', 'address',
            'village', 'city', 'tag', 'dob', 'gstin', 'ref_by', 'ref_by_display',
            'notes', 'is_active', 'created_at',
            'total_billed', 'total_paid', 'balance', 'bookings_count',
            'last_transaction_date'
        ]
        read_only_fields = [
            'id', 'customer_id', 'ref_by', 'created_at',
            'total_billed', 'total_paid', 'balance', 'bookings_count',
            'last_transaction_date'
        ]
        extra_kwargs = {
            'name': {'required': True},
            'contact': {'required': True},
            'tag': {'required': True},
        }

    def get_total_billed(self, obj):
        return obj.ledger_entries.aggregate(total=models.Sum('debit'))['total'] or 0

    def get_total_paid(self, obj):
        return obj.ledger_entries.aggregate(total=models.Sum('credit'))['total'] or 0

    def get_balance(self, obj):
        return self.get_total_billed(obj) - self.get_total_paid(obj)

    def get_bookings_count(self, obj):
        return obj.bookings.count()

    def get_last_transaction_date(self, obj):
        last = obj.ledger_entries.order_by('-date').first()
        return last.date if last else None


class CustomerPaymentSerializer(serializers.ModelSerializer):
    # Write-only fields that map to ForeignKeys (frontend sends customerId & bookingId)
    customer_id = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.all(),
        source='customer',
        write_only=True,
        required=True,
        error_messages={'required': 'Customer ID is required.'}
    )
    booking_id = serializers.PrimaryKeyRelatedField(
        queryset=Booking.objects.all(),
        source='booking',
        write_only=True,
        required=False,
        allow_null=True
    )

    # Read-only fields to output the related object IDs in the response
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    booking = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CustomerPayment
        fields = [
            'id', 'payment_id', 'customer', 'customer_id',
            'booking', 'booking_id',
            'date', 'amount', 'mode', 'reference', 'received_by', 'note'
        ]
        read_only_fields = ['payment_id', 'received_by', 'date', 'customer', 'booking']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LedgerEntry
        fields = '__all__'


class CustomerLedgerSerializer(serializers.Serializer):
    customer = CustomerSerializer()
    transactions = LedgerEntrySerializer(many=True)
    payments = CustomerPaymentSerializer(many=True)
    bookings = BookingSerializer(many=True)