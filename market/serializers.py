from rest_framework import serializers
from .models import Item

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        # These are the fields the Mobile App will see
        fields = ('id', 'title', 'description', 'price', 'image', 'is_sold', 'created_at')
