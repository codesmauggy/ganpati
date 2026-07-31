from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from .models import Worker

User = get_user_model()

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        worker = super().create(validated_data)
        # Create a corresponding User with staff role
        username = f"staff_{worker.worker_id}"
        user = User(
            username=username,
            fullName=worker.name,
            role='staff',
            is_active=True,
        )
        user.set_unusable_password()
        user.save()
        return worker