from rest_framework import serializers
from django.db import transaction, models
from .models import Booking, RetailBooking, WholesaleBooking, OrderItem, Tempo
from catalog.models import Model
from customers.models import Customer, LedgerEntry, CustomerPayment


class OrderItemSerializer(serializers.ModelSerializer):
    model_sku = serializers.CharField(write_only=True, required=True)
    unit_price = serializers.IntegerField(required=False)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'model', 'model_sku', 'qty', 'unit_price', 'line_total']
        read_only_fields = ['id', 'model']

    def get_line_total(self, obj):
        return obj.line_total


# ---- Generic BookingSerializer for ledger / list views ----
class BookingSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    collector = serializers.PrimaryKeyRelatedField(read_only=True)
    model_name = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    #channel = serializers.ReadOnlyField(source='channel')
    channel = serializers.ReadOnlyField()
    collector_fullName = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'customer', 'customer_id', 'customer_name', 'mobile', 'village',
            'advance', 'status', 'channel', 'collector', 'collector_fullName', 'date', 'pickup_date', 'notes',
            'model_name', 'qty', 'amount'
        ]
        read_only_fields = ['collector', 'collector_fullName', 'date', 'booking_id', 'customer',
                            'model_name', 'qty', 'amount', 'channel']

    def get_collector_fullName(self, obj):
        if obj.collector:
            return obj.collector.get_full_name() or obj.collector.username
        return None

    def get_model_name(self, obj):
        if hasattr(obj, 'retailbooking'):
            return obj.retailbooking.model.name
        elif hasattr(obj, 'wholesalebooking'):
            return obj.wholesalebooking.model_names
        return None

    def get_qty(self, obj):
        if hasattr(obj, 'retailbooking'):
            return obj.retailbooking.qty
        elif hasattr(obj, 'wholesalebooking'):
            return obj.wholesalebooking.total_qty
        return None

    def get_amount(self, obj):
        if hasattr(obj, 'retailbooking'):
            return obj.retailbooking.amount
        elif hasattr(obj, 'wholesalebooking'):
            return obj.wholesalebooking.amount
        return None


# ---- Retail Booking Serializer ----
class RetailBookingSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    collector = serializers.PrimaryKeyRelatedField(read_only=True)
    model_sku = serializers.CharField(write_only=True, required=True)
    channel = serializers.ReadOnlyField(default='Retail')

    customer_name = serializers.CharField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)

    model_name = serializers.SerializerMethodField()
    # ADD collector_fullName field
    collector_fullName = serializers.SerializerMethodField()

    class Meta:
        model = RetailBooking
        fields = [
            'id', 'booking_id', 'customer', 'customer_id', 'customer_name', 'mobile', 'village',
            'advance', 'status', 'collector', 'collector_fullName', 'date', 'pickup_date', 'notes',
            'model', 'model_sku', 'qty', 'amount', 'channel', 'model_name'
        ]
        read_only_fields = ['collector', 'collector_fullName', 'date', 'booking_id', 'customer',
                            'model', 'channel', 'model_name']

    def get_model_name(self, obj):
        return obj.model.name if obj.model else None

    # ADD the same method for collector_fullName
    def get_collector_fullName(self, obj):
        if obj.collector:
            return obj.collector.get_full_name() or obj.collector.username
        return None

    def validate(self, data):
        allowed = ['Booked', 'Loading', 'Dispatched', 'Delivered', 'Cancelled']
        if data.get('status') not in allowed:
            raise serializers.ValidationError({'status': f'Invalid for Retail. Allowed: {", ".join(allowed)}'})

        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name')
        mobile = data.get('mobile')
        if not customer_id and (not customer_name or not mobile):
            raise serializers.ValidationError({
                'detail': 'Either customer_id OR both customer_name and mobile are required.'
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        model_sku = validated_data.pop('model_sku')
        request = self.context.get('request')
        print("Incoming retail data:", validated_data)
        if not request or not request.user:
            raise serializers.ValidationError({'detail': 'Authenticated user required.'})

        try:
            model = Model.objects.get(sku=model_sku)
        except Model.DoesNotExist:
            raise serializers.ValidationError({'model_sku': 'Model not found.'})

        qty = validated_data.get('qty')
        amount = validated_data.get('amount')
        if amount is None:
            amount = qty * model.selling_price
        validated_data['amount'] = amount
        validated_data['model'] = model

        customer_id = validated_data.pop('customer_id', None)
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                validated_data['customer'] = customer
                validated_data['customer_name'] = customer.name
                validated_data['mobile'] = customer.contact
                if not validated_data.get('village'):
                    validated_data['village'] = customer.village or ''
            except Customer.DoesNotExist:
                raise serializers.ValidationError({'customer_id': 'Customer not found.'})
        else:
            name = validated_data.get('customer_name')
            mobile = validated_data.get('mobile')
            village = validated_data.get('village', '')
            if not name or not mobile:
                raise serializers.ValidationError({'detail': 'Both name and mobile required for new customer.'})
            customer, _ = Customer.objects.get_or_create(
                contact=mobile,
                defaults={'name': name, 'village': village, 'tag': 'Retail'}
            )
            validated_data['customer'] = customer
            validated_data['customer_name'] = customer.name
            validated_data['mobile'] = customer.contact
            validated_data['village'] = customer.village

        validated_data['collector'] = request.user
        booking = RetailBooking.objects.create(**validated_data)

        model.available -= booking.qty
        model.retail_sold += booking.qty
        model.save(update_fields=['available', 'retail_sold'])

        LedgerEntry.objects.create(
            customer=booking.customer,
            date=booking.date,
            type='Booking',
            reference=booking.booking_id,
            description=f"Retail order {booking.booking_id}",
            debit=booking.amount,
            credit=0,
            recorded_by=booking.collector
        )

        if booking.advance > 0:
            payment = CustomerPayment.objects.create(
                customer=booking.customer,
                date=booking.date,
                amount=booking.advance,
                mode='Cash',
                reference='',
                booking=booking,
                received_by=booking.collector,
                note=f"Advance payment for {booking.booking_id}"
            )
            LedgerEntry.objects.create(
                customer=booking.customer,
                date=booking.date,
                type='Payment',
                reference=payment.payment_id,
                description=f"Advance for {booking.booking_id}",
                debit=0,
                credit=booking.advance,
                recorded_by=booking.collector
            )

        return booking

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.advance = validated_data.get('advance', instance.advance)
        instance.pickup_date = validated_data.get('pickup_date', instance.pickup_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        return instance


# ---- Wholesale Booking Serializer ----
class WholesaleBookingSerializer(serializers.ModelSerializer):
    customer_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    collector = serializers.PrimaryKeyRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, required=True)
    channel = serializers.ReadOnlyField(default='Wholesale')

    customer_name = serializers.CharField(required=False, allow_blank=True)
    mobile = serializers.CharField(required=False, allow_blank=True)
    village = serializers.CharField(required=False, allow_blank=True)

    model_name = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()
    # ADD collector_fullName
    collector_fullName = serializers.SerializerMethodField()

    class Meta:
        model = WholesaleBooking
        fields = [
            'id', 'booking_id', 'customer', 'customer_id', 'customer_name', 'mobile', 'village',
            'advance', 'status', 'collector', 'collector_fullName', 'date', 'pickup_date', 'notes',
            'items', 'channel', 'model_name', 'qty', 'amount'
        ]
        read_only_fields = ['collector', 'collector_fullName', 'date', 'booking_id', 'customer',
                            'channel', 'model_name', 'qty', 'amount']

    def get_model_name(self, obj):
        return obj.model_names

    def get_qty(self, obj):
        return obj.total_qty

    # ADD the same method
    def get_collector_fullName(self, obj):
        if obj.collector:
            name = obj.collector.get_full_name() or obj.collector.username
            return name
        return None

    def validate(self, data):
        allowed = ['Booked', 'Loading', 'Dispatched', 'Delivered', 'Cancelled', 'Returned']
        if data.get('status') not in allowed:
            raise serializers.ValidationError({'status': f'Invalid for Wholesale. Allowed: {", ".join(allowed)}'})
        if not data.get('items'):
            raise serializers.ValidationError({'items': 'At least one item is required.'})

        customer_id = data.get('customer_id')
        customer_name = data.get('customer_name')
        mobile = data.get('mobile')
        if not customer_id and (not customer_name or not mobile):
            raise serializers.ValidationError({
                'detail': 'Either customer_id OR both customer_name and mobile are required.'
            })
        return data

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        request = self.context.get('request')
        print("Incoming retail data:", validated_data)
        if not request or not request.user:
            raise serializers.ValidationError({'detail': 'Authenticated user required.'})

        customer_id = validated_data.pop('customer_id', None)
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                validated_data['customer'] = customer
                validated_data['customer_name'] = customer.name
                validated_data['mobile'] = customer.contact
                if not validated_data.get('village'):
                    validated_data['village'] = customer.village or ''
            except Customer.DoesNotExist:
                raise serializers.ValidationError({'customer_id': 'Customer not found.'})
        else:
            name = validated_data.get('customer_name')
            mobile = validated_data.get('mobile')
            village = validated_data.get('village', '')
            if not name or not mobile:
                raise serializers.ValidationError({'detail': 'Both name and mobile required for new customer.'})
            customer, _ = Customer.objects.get_or_create(
                contact=mobile,
                defaults={'name': name, 'village': village, 'tag': 'Wholesale'}
            )
            validated_data['customer'] = customer
            validated_data['customer_name'] = customer.name
            validated_data['mobile'] = customer.contact
            validated_data['village'] = customer.village

        if customer.tag != 'Wholesale':
            customer.tag = 'Wholesale'
            customer.save(update_fields=['tag'])

        validated_data['collector'] = request.user
        booking = WholesaleBooking.objects.create(**validated_data)

        total_amount = 0
        for item_data in items_data:
            model_sku = item_data.pop('model_sku')
            try:
                model = Model.objects.get(sku=model_sku)
            except Model.DoesNotExist:
                raise serializers.ValidationError({'items': f'Model with SKU {model_sku} not found.'})
            qty = item_data.get('qty')
            unit_price = item_data.get('unit_price', model.selling_price)
            OrderItem.objects.create(
                wholesale_booking=booking,
                model=model,
                qty=qty,
                unit_price=unit_price
            )
            total_amount += qty * unit_price

            model.available -= qty
            model.wholesale_sold += qty
            model.save(update_fields=['available', 'wholesale_sold'])

        booking.amount = total_amount
        booking.save(update_fields=['amount'])

        LedgerEntry.objects.create(
            customer=booking.customer,
            date=booking.date,
            type='Booking',
            reference=booking.booking_id,
            description=f"Wholesale order {booking.booking_id}",
            debit=total_amount,
            credit=0,
            recorded_by=booking.collector
        )

        if booking.advance > 0:
            payment = CustomerPayment.objects.create(
                customer=booking.customer,
                date=booking.date,
                amount=booking.advance,
                mode='Cash',
                reference='',
                booking=booking,
                received_by=booking.collector,
                note=f"Advance payment for {booking.booking_id}"
            )
            LedgerEntry.objects.create(
                customer=booking.customer,
                date=booking.date,
                type='Payment',
                reference=payment.payment_id,
                description=f"Advance for {booking.booking_id}",
                debit=0,
                credit=booking.advance,
                recorded_by=booking.collector
            )

        return booking

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.advance = validated_data.get('advance', instance.advance)
        instance.pickup_date = validated_data.get('pickup_date', instance.pickup_date)
        instance.notes = validated_data.get('notes', instance.notes)
        instance.save()
        return instance


# ---- Tempo Serializer ----
class TempoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tempo
        fields = '__all__'