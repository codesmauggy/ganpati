from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'fullName', 'role', 'email']
        read_only_fields = ['fullName']   # computed in model