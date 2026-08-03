from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import OrderItem, WholesaleBooking


@receiver([post_save, post_delete], sender=OrderItem)
def update_wholesale_booking_amount(sender, instance, **kwargs):
    """
    Recalculate the WholesaleBooking.amount field whenever an OrderItem
    is added, updated, or deleted.
    """
    booking = instance.wholesale_booking
    total = 0
    for item in booking.items.all():
        total += item.qty * item.unit_price
    if booking.amount != total:
        booking.amount = total
        booking.save(update_fields=['amount'])