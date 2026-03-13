from rest_framework import serializers
from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = (
            'id', 'title', 'description', 'price',
            'product_type', 'gender', 'size', 'brand', 'color',
            'barcode', 'condition', 'image', 'is_sold', 'created_at',
        )
