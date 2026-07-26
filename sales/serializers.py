from rest_framework import serializers
from .models import Booking, Tempo
from catalog.models import Model
from customers.models import Customer
from django.db import models as django_models

class BookingSerializer(serializers.ModelSerializer):
    model_name = serializers.CharField(source='model.name', read_only=True)
    # Write-only fields (frontend sends modelSku, customerId, parser converts to snake_case)
    model_sku = serializers.CharField(write_only=True, required=True)
    customer_id = serializers.CharField(write_only=True, required=False, allow_null=True)
    # Read-only output fields
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    model = serializers.PrimaryKeyRelatedField(read_only=True)
    collector = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'booking_id', 'customer', 'customer_id', 'customer_name', 'mobile', 'village',
            'model', 'model_sku', 'model_name', 'qty', 'amount', 'advance', 'status', 'channel',
            'collector', 'date', 'pickup_date'
        ]
        read_only_fields = ['amount', 'collector', 'date', 'booking_id', 'customer', 'model']

    def create(self, validated_data):
        model_sku = validated_data.pop('model_sku')
        customer_id = validated_data.pop('customer_id', None)

        # Resolve model by SKU
        try:
            model = Model.objects.get(sku=model_sku)
        except Model.DoesNotExist:
            raise serializers.ValidationError({'model_sku': 'Model with this SKU does not exist.'})
        validated_data['model'] = model

        # Handle customer
        if customer_id:
            try:
                customer = Customer.objects.get(customer_id=customer_id)
                validated_data['customer'] = customer
                # Update denormalized fields from customer
                validated_data['customer_name'] = customer.name
                validated_data['mobile'] = customer.contact
                if not validated_data.get('village') and customer.village:
                    validated_data['village'] = customer.village
            except Customer.DoesNotExist:
                raise serializers.ValidationError({'customer_id': 'Customer not found.'})
        else:
            # Create or get customer from provided name/mobile
            name = validated_data.get('customer_name')
            mobile = validated_data.get('mobile')
            village = validated_data.get('village', '')
            if not name or not mobile:
                raise serializers.ValidationError({'detail': 'Either customer_id or customer_name and mobile must be provided.'})
            customer, _ = Customer.objects.get_or_create(
                contact=mobile,
                defaults={'name': name, 'village': village, 'tag': validated_data.get('channel', 'Retail')}
            )
            validated_data['customer'] = customer

        # Set collector from request.user (passed via context)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['collector'] = request.user
        else:
            raise serializers.ValidationError({'detail': 'Authenticated user required.'})

        # Compute amount
        qty = validated_data.get('qty', 1)
        amount = qty * model.selling_price
        validated_data['amount'] = amount

        # Save booking
        booking = Booking(**validated_data)
        booking.save()

        # Decrement stock
        model.available -= booking.qty
        model.save(update_fields=['available'])
        # Update wholesale/retail sold counts
        if booking.channel == 'Wholesale':
            model.wholesale_sold += booking.qty
        else:
            model.retail_sold += booking.qty
        model.save(update_fields=['wholesale_sold', 'retail_sold'])

        # Create ledger entries for customer
        from customers.models import LedgerEntry, CustomerPayment
        LedgerEntry.objects.create(
            customer=customer,
            date=booking.date,
            type='Booking',
            reference=booking.booking_id,
            description=f"{model.name} x {booking.qty}",
            debit=amount,
            credit=0,
            recorded_by=booking.collector
        )
        if booking.advance > 0:
            payment = CustomerPayment.objects.create(
                customer=customer,
                date=booking.date,
                amount=booking.advance,
                mode='Cash',
                reference='',
                booking=booking,
                received_by=booking.collector,
                note='Advance payment'
            )
            LedgerEntry.objects.create(
                customer=customer,
                date=booking.date,
                type='Payment',
                reference=payment.payment_id,
                description=f"Advance payment for {booking.booking_id}",
                debit=0,
                credit=booking.advance,
                recorded_by=booking.collector
            )
        return booking

    def update(self, instance, validated_data):
        validated_data.pop('model_sku', None)
        validated_data.pop('customer_id', None)
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if 'advance' in validated_data:
            instance.advance = validated_data['advance']
        if 'pickup_date' in validated_data:
            instance.pickup_date = validated_data['pickup_date']
        instance.save()
        return instance

class TempoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tempo
        fields = '__all__'