from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from accounts.decorators import customer_required, vendor_required
from products.models import Product, PromotionDay
from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from notifications.models import Notification
from accounts.models import SokohubCard
from django.utils import timezone
from decimal import Decimal

@customer_required
def checkout_cart(request):
    """
    Handle checkout for all items in the cart
    """
    cart, created = Cart.objects.get_or_create(customer=request.user)
    items = cart.items.all()

    if not items:
        messages.error(request, 'Your cart is empty.')
        return redirect('view_cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Group items by vendor
                    vendor_items_map = {}
                    for item in items:
                        vendor = item.product.vendor
                        if vendor not in vendor_items_map:
                            vendor_items_map[vendor] = []
                        vendor_items_map[vendor].append(item)

                    # Check stock for all items
                    for item in items:
                        if item.product.stock < item.quantity:
                            messages.error(request, f'Sorry, only {item.product.stock} items of {item.product.name} available.')
                            return redirect('checkout_cart')

                    # Calculate grand total for all vendors
                    grand_total = Decimal('0.00')
                    is_promotion = PromotionDay.objects.filter(date=timezone.now().date()).exists()
                    has_card = SokohubCard.objects.filter(user=request.user, status='approved', is_active=True).exists()
                    
                    for vendor, v_items in vendor_items_map.items():
                        v_total = sum(item.get_total_price() for item in v_items)
                        if is_promotion and has_card:
                            v_total = v_total * Decimal('0.95')
                        grand_total += v_total

                    # Handle Virtual Card payment deduction
                    payment_method = form.cleaned_data['payment_method']
                    if payment_method == 'virtual_card':
                        if not has_card:
                            messages.error(request, "You do not have a Sokohub Card to use this payment method.")
                            return redirect('checkout_cart')
                        
                        user_card = SokohubCard.objects.get(user=request.user)
                        if user_card.balance < grand_total:
                            messages.error(request, f"Insufficient balance on your Sokohub Card. (Balance: ${user_card.balance})")
                            return redirect('checkout_cart')
                        
                        # Deduct from balance
                        user_card.balance -= grand_total
                        user_card.save()

                    created_order_ids = []
                    for vendor, v_items in vendor_items_map.items():
                        # Calculate vendor subtotal
                        vendor_total = sum(item.get_total_price() for item in v_items)
                        
                        if is_promotion and has_card:
                            vendor_total = vendor_total * Decimal('0.95')

                        # Create order for this vendor
                        order = Order.objects.create(
                            customer=request.user,
                            vendor=vendor,
                            total=vendor_total,
                            delivery_address=form.cleaned_data['delivery_address'],
                            phone=form.cleaned_data['phone'],
                            payment_method=payment_method
                        )
                        
                        # If paid with virtual card, mark as paid immediately
                        if payment_method == 'virtual_card':
                            order.status = 'paid'
                            order.payment_status = 'paid'
                            order.transaction_id = f"VC-{order.id}-{user_card.virtual_id[-4:]}"
                            order.save()

                        created_order_ids.append(str(order.id))

                        # Create order items and update stock
                        for item in v_items:
                            OrderItem.objects.create(
                                order=order,
                                product=item.product,
                                quantity=item.quantity,
                                price=item.product.price
                            )
                            item.product.stock -= item.quantity
                            item.product.save()

                        # Create notification for vendor
                        Notification.objects.create(
                            user=vendor,
                            title="New Order Received",
                            message=f"You have a new order (# {order.id}) for {v_items.__len__()} items.",
                            notification_type='order_update',
                            target_url=f"/orders/vendor/orders/transaction/{order.id}/"
                        )

                    # Clear cart
                    items.delete()

                    order_str = ", ".join(created_order_ids)
                    messages.success(request, f'Order(s) placed successfully! Order number(s): #{order_str}')
                    # Redirect to confirmation with the first order ID (we'll update confirmation to handle context if needed)
                    return redirect('order_confirmation', order_id=created_order_ids[0])

            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
    else:
        initial_data = {
            'phone': request.user.phone or '',
            'delivery_address': request.user.location or '',
        }
        form = CheckoutForm(initial=initial_data)

    is_promotion = PromotionDay.objects.filter(date=timezone.now().date()).exists()
    card = SokohubCard.objects.filter(user=request.user, status='approved', is_active=True).first()
    
    total = cart.get_total_price()
    discount_amount = Decimal('0.00')
    discounted_total = total
    
    if is_promotion and card:
        discount_amount = total * Decimal('0.05')
        discounted_total = total - discount_amount

    # Calculate default payment method
    default_method = form['payment_method'].value()

    context = {
        'cart': cart,
        'items': items,
        'form': form,
        'title': 'Cart Checkout',
        'is_cart_checkout': True,
        'is_promotion': is_promotion,
        'card': card,
        'total': total,
        'discount_amount': discount_amount,
        'discounted_total': discounted_total,
        'default_method': default_method
    }
    return render(request, 'orders/checkout.html', context)

@customer_required
def checkout(request, product_id):
    """
    Handle single product checkout
    """
    product = get_object_or_404(Product, id=product_id, status='active')

    # Check if product is in stock
    if not product.is_in_stock():
        messages.error(request, 'Sorry, this product is currently out of stock.')
        return redirect('product_detail', product_id=product_id)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    quantity = form.cleaned_data.get('quantity') or 1

                    # Check stock availability again (prevent race condition)
                    if product.stock < quantity:
                        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
                        return redirect('checkout', product_id=product_id)

                    # Calculate total
                    total = product.price * quantity

                    # Apply 5% discount for Sokohub Card holders on Promotion Days
                    is_promotion = PromotionDay.objects.filter(date=timezone.now().date()).exists()
                    has_card = SokohubCard.objects.filter(user=request.user, status='approved', is_active=True).exists()
                    
                    if is_promotion and has_card:
                        total = total * Decimal('0.95')

                    # Handle Virtual Card payment deduction
                    payment_method = form.cleaned_data['payment_method']
                    if payment_method == 'virtual_card':
                        if not has_card:
                            messages.error(request, "You do not have a Sokohub Card to use this payment method.")
                            return redirect('checkout', product_id=product.id)
                        
                        user_card = SokohubCard.objects.get(user=request.user)
                        if user_card.balance < total:
                            messages.error(request, f"Insufficient balance on your Sokohub Card. (Balance: ${user_card.balance})")
                            return redirect('checkout', product_id=product.id)
                        
                        # Deduct from balance
                        user_card.balance -= total
                        user_card.save()

                    # Create order
                    order = Order.objects.create(
                        customer=request.user,
                        vendor=product.vendor,
                        total=total,
                        delivery_address=form.cleaned_data['delivery_address'],
                        phone=form.cleaned_data['phone'],
                        payment_method=payment_method
                    )
                    
                    # If paid with virtual card, mark as paid immediately
                    if payment_method == 'virtual_card':
                        order.status = 'paid'
                        order.payment_status = 'paid'
                        order.transaction_id = f"VC-{order.id}-{user_card.virtual_id[-4:]}"
                        order.save()

                    # Create order item
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )

                    # Update product stock
                    product.stock -= quantity
                    product.save()

                    # Create notification for vendor
                    Notification.objects.create(
                        user=product.vendor,
                        title="New Order Received",
                        message=f"You have a new order (# {order.id}) for {quantity}x {product.name}.",
                        notification_type='order_update',
                        target_url=f"/orders/vendor/orders/transaction/{order.id}/"
                    )

                    messages.success(request, f'Order placed successfully! Your order number is #{order.id}')
                    return redirect('order_confirmation', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')

    else:
        # Pre-fill form with user data
        initial_data = {
            'phone': request.user.phone or '',
            'delivery_address': request.user.location or '',
            'quantity': 1
        }
        form = CheckoutForm(initial=initial_data)

    is_promotion = PromotionDay.objects.filter(date=timezone.now().date()).exists()
    card = SokohubCard.objects.filter(user=request.user, status='approved', is_active=True).first()
    
    # We use initial quantity 1 for display
    unit_price = product.price
    discount_amount = Decimal('0.00')
    discounted_unit_price = unit_price
    
    if is_promotion and card:
        discount_amount = unit_price * Decimal('0.05')
        discounted_unit_price = unit_price - discount_amount

    # Calculate default payment method
    default_method = form['payment_method'].value()

    context = {
        'product': product,
        'form': form,
        'title': 'Checkout',
        'is_cart_checkout': False,
        'is_promotion': is_promotion,
        'card': card,
        'unit_price': unit_price,
        'total': unit_price,
        'discount_amount': discount_amount,
        'discounted_unit_price': discounted_unit_price,
        'default_method': default_method
    }
    return render(request, 'orders/checkout.html', context)

@customer_required
def order_confirmation(request, order_id):
    """
    Display order confirmation page
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    context = {
        'order': order,
        'title': 'Order Confirmation'
    }
    return render(request, 'orders/order_confirmation.html', context)

@customer_required
def customer_orders(request):
    """
    Display all orders for the logged-in customer
    """
    orders = Order.objects.filter(customer=request.user).prefetch_related('items', 'items__product')
    context = {
        'orders': orders,
        'title': 'My Orders'
    }
    return render(request, 'orders/customer_orders.html', context)

@customer_required
def order_detail(request, order_id):
    """
    Display detailed view of a specific order
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    context = {
        'order': order,
        'title': f'Order #{order.id}'
    }
    return render(request, 'orders/order_detail.html', context)

@customer_required
def customer_orders(request):
    """Customer's order history"""
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    return render(request, 'orders/customer_orders.html', {'orders': orders})

@vendor_required
def vendor_orders(request):
    """Vendor's order management page"""
    # Get all orders for this vendor
    orders = Order.objects.filter(
        vendor=request.user
    ).prefetch_related('items', 'items__product').order_by('-created_at')
    
    # Count pending orders for notifications
    pending_count = orders.filter(status='pending').count()
    
    context = {
        'orders': orders,
        'pending_count': pending_count,
        'title': 'Vendor Orders'
    }
    return render(request, 'orders/vendor_orders.html', context)

@vendor_required
def approve_order(request, order_id):
    """Vendor approves an order"""
    order = get_object_or_404(Order, id=order_id, vendor=request.user)
    
    if order.can_be_confirmed():
        order.status = 'approved'
        order.save()
        
        # Note: Stock was already reduced during checkout in the original code, 
        # but let's ensure it's handled consistently. 
        # Actually, the original code reduces stock during order creation (checkout views).
        
        messages.success(request, 
            f"Order #{order.id} approved! " +
            f"Customer has been notified."
        )

        # Create notification for customer
        Notification.objects.create(
            user=order.customer,
            title="Order Approved",
            message=f"Your order #{order.id} has been approved by the vendor. You can now download your receipt.",
            notification_type='order_update',
            target_url=reverse('order_detail', kwargs={'order_id': order.id})
        )

        # Automatically generate Receipt
        from django.utils.crypto import get_random_string
        from .models import Receipt
        receipt_no = f"REC-{order.id}-{get_random_string(5).upper()}"
        Receipt.objects.get_or_create(order=order, defaults={'receipt_number': receipt_no})
        
        print(f"=== ORDER APPROVED ===")
        print(f"Order: #{order.id}")
        print(f"Vendor: {request.user.username}")
        print(f"Customer: {order.customer.username}")
        
    else:
        messages.error(request, "This order cannot be approved. Ensure it has been paid first.")
    
    return redirect('transaction_detail', order_id=order.id)



@vendor_required
def cancel_order(request, order_id):
    """Vendor cancels an order"""
    order = get_object_or_404(Order, id=order_id, vendor=request.user)
    
    if order.can_be_cancelled():
        old_status = order.status
        order.status = 'cancelled'
        order.save()
        
        # If order was confirmed, restore stock
        if old_status == 'confirmed':
            for item in order.items.all():
                item.product.stock += item.quantity
                item.product.save()
        
        # REFUND: If paid with virtual card, add money back to card balance
        if order.payment_method == 'virtual_card' and old_status in ['paid', 'approved', 'shipped']:
            try:
                user_card = SokohubCard.objects.get(user=order.customer)
                user_card.balance += order.total
                user_card.save()

                # Add a refund notification for customer
                Notification.objects.create(
                    user=order.customer,
                    title="Order Refunded",
                    message=f"Your payment of ${order.total} for order #{order.id} has been refunded to your Sokohub Card.",
                    notification_type='order_update',
                    target_url=reverse('sokohub_card_details')
                )
            except SokohubCard.DoesNotExist:
                pass
        
        messages.success(request, f"Order #{order.id} has been cancelled.")

        # Create notification for customer
        Notification.objects.create(
            user=order.customer,
            title="Order Cancelled",
            message=f"Your order #{order.id} has been cancelled by the vendor.",
            notification_type='order_update',
            target_url=reverse('order_detail', kwargs={'order_id': order.id})
        )
    else:
        messages.error(request, "This order cannot be cancelled.")
    
    return redirect('vendor_orders')

@customer_required
def pay_order(request, order_id):
    """
    Simulate payment for an order
    """
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status == 'pending':
        # Simulate payment processing
        order.status = 'paid'
        order.payment_status = 'paid'
        order.transaction_id = f"TRX-{order.id}-SIM"
        order.save()
        
        # Notify vendor
        Notification.objects.create(
            user=order.vendor,
            title="Order Paid",
            message=f"Order #{order.id} has been paid. Click to review and approve.",
            notification_type='order_update',
            target_url=f"/orders/vendor/orders/transaction/{order.id}/"
        )
        
        messages.success(request, f"Payment successful! Order #{order.id} is now awaiting vendor approval.")
    else:
        messages.error(request, "This order is not in a payable state.")
        
    return redirect('order_detail', order_id=order.id)


@customer_required
def download_receipt(request, order_id):
    """
    View to display/download the receipt for an approved order
    """
    from .models import Receipt
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    
    if order.status not in ['approved', 'delivered', 'shipped']:
        messages.error(request, "A receipt is not yet available for this order.")
        return redirect('order_detail', order_id=order.id)
        
    receipt = get_object_or_404(Receipt, order=order)
    
    context = {
        'receipt': receipt,
        'title': f"Receipt {receipt.receipt_number}"
    }
    return render(request, 'orders/receipt_detail.html', context)

@vendor_required
def transaction_detail(request, order_id):
    """
    Vendor view for full transaction details before approval
    """
    order = get_object_or_404(Order, id=order_id, vendor=request.user)
    context = {
        'order': order,
        'title': f'Transaction Detail - Order #{order.id}'
    }
    return render(request, 'orders/transaction_detail.html', context)

@login_required
def check_stock(request, product_id):
    """
    JSON endpoint to check product stock
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id)
        return JsonResponse({
            'stock': product.stock,
            'is_in_stock': product.is_in_stock(),
            'max_quantity': product.stock
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)