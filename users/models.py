from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


# NEW: Review Model
class Review(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]  # 1 to 5

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One review per buyer per seller
        unique_together = ('seller', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.username} → {self.seller.username} ({self.rating}★)"