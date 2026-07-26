from django.db import models
from django.conf import settings
from catalog.models import Model
from customers.models import Customer

class Booking(models.Model):
    STATUS_CHOICES = (
        ('Booked', 'Booked'),
        ('Advance Paid', 'Advance Paid'),
        ('Loading', 'Loading'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
        ('Pending', 'Pending'),
    )
    CHANNEL_CHOICES = (
        ('Wholesale', 'Wholesale'),
        ('Retail', 'Retail'),
    )
    booking_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    customer_name = models.CharField(max_length=100)  # denormalized
    mobile = models.CharField(max_length=15)
    village = models.CharField(max_length=100, blank=True)
    model = models.ForeignKey(Model, on_delete=models.PROTECT)
    qty = models.PositiveIntegerField()
    amount = models.IntegerField()  # computed
    advance = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Booked')
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)
    collector = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='collected_bookings')
    date = models.DateField(auto_now_add=True)
    pickup_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.booking_id:
            # generate BK-XXXX (simple increment)
            last = Booking.objects.all().order_by('id').last()
            if last:
                num = int(last.booking_id.split('-')[1]) + 1
            else:
                num = 1
            self.booking_id = f"BK-{num:04d}"
        # compute amount
        if self.model:
            self.amount = self.qty * self.model.selling_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.booking_id

class Tempo(models.Model):
    STATUS_CHOICES = (
        ('Loading', 'Loading'),
        ('Dispatched', 'Dispatched'),
        ('Delivered', 'Delivered'),
    )
    tempo_id = models.CharField(max_length=20, unique=True)
    tempo = models.CharField(max_length=50)  # vehicle number
    place = models.CharField(max_length=100)
    items = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Loading')
    bookings = models.ManyToManyField(Booking, related_name='tempos', blank=True)

    def __str__(self):
        return self.tempo_id