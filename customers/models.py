from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Customer(models.Model):
    TAG_CHOICES = (
        ('Retail', 'Retail'),
        ('Wholesale', 'Wholesale'),
    )
    customer_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    alt_contact = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    village = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)
    dob = models.DateField(null=True, blank=True)
    gstin = models.CharField(max_length=20, blank=True)
    ref_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='referred_customers')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last = Customer.objects.all().order_by('id').last()
            if last:
                num = int(last.customer_id.split('-')[1]) + 1
            else:
                num = 1
            self.customer_id = f"C-{num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CustomerPayment(models.Model):
    MODE_CHOICES = (
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Card', 'Card'),
    )
    payment_id = models.CharField(max_length=20, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='payments')
    date = models.DateField(auto_now_add=True)
    amount = models.IntegerField(validators=[MinValueValidator(0)])
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    reference = models.CharField(max_length=100, blank=True)
    booking = models.ForeignKey('sales.Booking', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    note = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.payment_id:
            last = CustomerPayment.objects.all().order_by('id').last()
            if last:
                num = int(last.payment_id.split('-')[1]) + 1
            else:
                num = 1
            self.payment_id = f"PY-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.payment_id

class LedgerEntry(models.Model):
    TYPE_CHOICES = (
        ('Booking', 'Booking'),
        ('Payment', 'Payment'),
        ('Adjustment', 'Adjustment'),
        ('Return', 'Return'),
    )
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='ledger_entries')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    reference = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    debit = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    credit = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.name} - {self.type} - {self.reference}"