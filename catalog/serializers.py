from rest_framework import serializers
from .models import Model

class ModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Model
        fields = [
            'id', 'sku', 'name', 'category', 'size', 'photo',
            'purchase_price', 'selling_price', 'raw_material_cost',
            'available', 'low_stock_at', 'wholesale_sold', 'retail_sold'
        ]
        # camelCase is handled by the renderer/parser