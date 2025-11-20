from django.db import models
from django.conf import settings
from django.core.validators import URLValidator, MinValueValidator
from django.urls import reverse
import uuid

class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    )
    # Add UUID for security (hide sequential IDs)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    image_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        validators=[URLValidator()],
        help_text="Optional URL for the product image."
    )

    def get_image_display(self):
        if self.image_url:
            return self.image_url
        elif self.image:
            return self.image.url
        else:
            return None
    
    def __str__(self):
        return self.name

    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'vendor'},
        related_name='vendor_products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        default='products/default_product.png'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'product_uuid': self.uuid})

    def is_in_stock(self):
        return self.stock > 0 and self.status == 'active'

    def get_display_price(self):
        return f"${self.price}"

    def save(self, *args, **kwargs):
        # Auto-update status based on stock
        if self.stock == 0 and self.status == 'active':
            self.status = 'out_of_stock'
        elif self.stock > 0 and self.status == 'out_of_stock':
            self.status = 'active'
        super().save(*args, **kwargs)