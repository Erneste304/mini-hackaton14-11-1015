from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='customer'
    )
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'auth_user'  # This ensures we replace the default User model

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    def is_vendor(self):
        return self.user_type == 'vendor'

    def is_customer(self):
        return self.user_type == 'customer'