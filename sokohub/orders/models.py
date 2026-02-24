from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('approved', 'Approved'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('mtn', 'MTN Mobile Money'),
        ('tigo', 'Tigo Pesa'),
        ('virtual_card', 'Virtual Card'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'customer'},
        related_name='customer_orders'
    )
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'vendor'},
        related_name='vendor_orders',
        null=True,
        blank=True
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    delivery_address = models.TextField()
    phone = models.CharField(max_length=15)
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        null=True,
        blank=True
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    transaction_id = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def can_be_cancelled(self):
        """" order can not only be cancelled if not shipped and delivered """
        return self.status in ['pending', 'paid', 'approved']
        
    def can_be_confirmed(self):
        """" vendor can only confirm order if it is paid """
        return self.status == 'paid'
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.id} - {self.customer.username}"

    def get_status_color(self):
        status_colors = {
            'pending': 'warning',
            'paid': 'info',
            'approved': 'success',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return status_colors.get(self.status, 'secondary')

    def get_items_count(self):
        return self.items.count()


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    class Meta:
        unique_together = ['order', 'product']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order #{self.order.id})"

    def get_subtotal(self):
        return self.quantity * self.price


class Receipt(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} for Order #{self.order.id}"

    class Meta:
        ordering = ['-issued_at']