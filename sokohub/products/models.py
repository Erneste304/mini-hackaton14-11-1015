from django.db import models
from django.conf import settings
from django.core.validators import URLValidator, MinValueValidator
from django.urls import reverse
import uuid
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome class, e.g., fas fa-laptop", blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_list_by_category', args=[self.slug])


class Product(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('out_of_stock', 'Out of Stock'),
    )
    # Add UUID for security (hide sequential IDs)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        default='products/default_product.png'
    )

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
    
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'vendor'},
        related_name='vendor_products'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    is_trending = models.BooleanField(default=False)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    stock = models.PositiveIntegerField(default=0)
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
        # Auto-update status based on stock only in specific cases
        # 1. If stock becomes 0 and it was previously 'active', mark as 'out_of_stock'
        if self.stock == 0 and self.status == 'active':
            self.status = 'out_of_stock'
        # 2. If stock becomes > 0 and it was 'out_of_stock', mark as 'active'
        elif self.stock > 0 and self.status == 'out_of_stock':
            self.status = 'active'
            
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.name}"