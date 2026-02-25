from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('vendor', 'Vendor'),
        ('customer', 'Customer'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=255, blank=True)
    tin_number = models.CharField(max_length=9, blank=True, null=True, help_text="9-digit RRA TIN Number")

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


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # OTP is valid for 3 minutes
        expiration_time = self.created_at + timezone.timedelta(minutes=3)
        return timezone.now() <= expiration_time

    def __str__(self):
        return f"OTP for {self.email} - {self.otp}"

class SokohubCard(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('approved', 'Approved'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sokohub_card')
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    card_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    virtual_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_card_details(self):
        if not self.card_number:
            # Generate a 16-digit card number format: 5050 XXXX XXXX XXXX
            random_digits = ''.join(random.choices(string.digits, k=12))
            self.card_number = f"5050{random_digits}"
        
        if not self.virtual_id:
            # Generate a Virtual ID: SH-XXXXXX
            random_id = ''.join(random.choices(string.digits + string.ascii_uppercase, k=6))
            self.virtual_id = f"SH-{random_id}"
        self.save()

    def __str__(self):
        return f"Sokohub Card for {self.user.username} - {self.status}"

    class Meta:
        verbose_name = "Sokohub Card"
        verbose_name_plural = "Sokohub Cards"
