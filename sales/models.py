from django.db import models
from django.conf import settings
from catalog.models import Model
from customers.models import Customer

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Loading', 'Loading'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
        ('Cancelled', 'Cancelled'),
    )

    booking_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='bookings')
    customer_name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    village = models.CharField(max_length=100, blank=True)
    advance = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='collected_bookings')
    date = models.DateField(auto_now_add=True)
    pickup_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, default='')

    def save(self, *args, **kwargs):
        if not self.booking_id:
            last = Booking.objects.all().order_by('id').last()
            num = int(last.booking_id.split('-')[1]) + 1 if last else 1
            self.booking_id = f"BK-{num:04d}"
        super().save(*args, **kwargs)

    @property
    def channel(self):
        if hasattr(self, 'retailbooking'):
            return 'Retail'
        elif hasattr(self, 'wholesalebooking'):
            return 'Wholesale'
        return 'Unknown'

    def __str__(self):
        return self.booking_id


class RetailBooking(Booking):
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    amount = models.IntegerField()   # line total (qty * unit price)

    def __str__(self):
        return f"{self.booking_id} (Retail)"


class WholesaleBooking(Booking):
    # Stored total = sum(qty * unit_price) over all items
    amount = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.booking_id} (Wholesale)"

    @property
    def total_qty(self):
        return self.items.aggregate(total=models.Sum('qty'))['total'] or 0

    @property
    def model_names(self):
        names = self.items.values_list('model__name', flat=True)
        return ", ".join(names) if names else "No items"


class OrderItem(models.Model):
    wholesale_booking = models.ForeignKey(WholesaleBooking, on_delete=models.CASCADE, related_name='items')
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    unit_price = models.IntegerField()   # price per unit

    @property
    def line_total(self):
        # Guard against None values when object is not saved yet
        if self.qty is not None and self.unit_price is not None:
            return self.qty * self.unit_price
        return 0   # or return None if you prefer

    def __str__(self):
        return f"{self.wholesale_booking.booking_id} – {self.model.name} x {self.qty}"


class Tempo(models.Model):
    STATUS_CHOICES = (
        ('Loading', 'Loading'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    )
    tempo_id = models.CharField(max_length=20, unique=True)
    vehicle_number = models.CharField(max_length=50)
    place = models.CharField(max_length=100)
    items = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Loading')
    bookings = models.ManyToManyField(Booking, related_name='tempos', blank=True)

    def save(self, *args, **kwargs):
        if not self.tempo_id:
            last = Tempo.objects.all().order_by('id').last()
            num = int(last.tempo_id.split('-')[1]) + 1 if last else 1
            self.tempo_id = f"TP-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tempo_id