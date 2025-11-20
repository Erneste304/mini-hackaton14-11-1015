from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )

    user_type = models.CharField(max_length=20,choices=USER_TYPE_CHOICES,default='customer')
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=255, blank=True)
    
    
    # Enhanced profile fields
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    address = models.TextField(blank=True, help_text="Full delivery address")
    date_of_birth = models.DateField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Rwanda')

        # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'auth_user'  # This ensures we replace the default User model

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_vendor(self):
        return self.user_type == 'vendor'

    def is_customer(self):
        return self.user_type == 'customer'
    
    def get_full_address(self):
        parts = [self.address, self.city, self.country]
        return ', '.join(filter(None, parts))
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    

