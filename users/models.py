from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. RESTORE THE CUSTOM USER MODEL (This was missing!)
class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    
    # We keep location here for backward compatibility, 
    # but we will use the Profile location moving forward.
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username

# 2. ADD THE NEW PROFILE MODEL
class Profile(models.Model):
    # Link to the User class defined above
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, max_length=500)
    location = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Profile of {self.user.username}"