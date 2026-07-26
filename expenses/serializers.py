from rest_framework import serializers
from .models import Expense

class ExpenseSerializer(serializers.ModelSerializer):
    paid_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Expense
        fields = '__all__'