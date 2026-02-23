from django.db import models
from django.conf import settings # Best practice to refer to User model

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True) # URL-friendly name (e.g., /electronics/)

    class Meta:
        verbose_name_plural = "Categories" # Fixes grammar in Admin panel

    def __str__(self):
        return self.name

class Item(models.Model):
    CONDITION_CHOICES = (
        ('new', 'New'),
        ('used_good', 'Used - Good'),
        ('used_fair', 'Used - Fair'),
    )

    # Relationships
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    
    # Fields
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='item_images/', blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='used_good')
    is_sold = models.BooleanField(default=False)
    
    # Timestamps (Crucial for sorting)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title