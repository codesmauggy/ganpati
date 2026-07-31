from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Customer

User = get_user_model()

@receiver(post_save, sender=Customer)
def delete_user_for_customer(sender, instance, **kwargs):
    User.objects.filter(cid=instance.customer_id).delete()


@receiver(post_save, sender=Customer)
def create_user_for_customer(sender, instance, created, **kwargs):
    if created:
        role_map = {'Retail': 'customer', 'Wholesale': 'wholesaler'}
        role = role_map.get(instance.tag)
        if role:
            username = f"{instance.contact}"
            user = User(
                username=username,
                fullName=instance.name,
                role=role,
                cid=instance.customer_id,  
                is_active=True,
            )
            user.set_unusable_password()
            user.save()