from django.db import models
from django.conf import settings
from market.models import Item


class Conversation(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversations')
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller_conversations')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='buyer_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # One conversation per buyer-seller-item combo
        unique_together = ('item', 'seller', 'buyer')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.buyer.username} ↔ {self.seller.username} about {self.item.title}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"From {self.sender.username} at {self.created_at:%Y-%m-%d %H:%M}"