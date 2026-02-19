from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from accounts.decorators import customer_required, vendor_required
from products.models import Product
from cart.models import Cart
from .models import Order, OrderItem
from .forms import CheckoutForm
from notifications.models import Notification

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

                    created_order_ids = []
                    for vendor, v_items in vendor_items_map.items():
                        # Calculate vendor subtotal
                        vendor_total = sum(item.get_total_price() for item in v_items)
                        
                        # Create order for this vendor
                        order = Order.objects.create(
                            customer=request.user,
                            vendor=vendor,
                            total=vendor_total,
                            delivery_address=form.cleaned_data['delivery_address'],
                            phone=form.cleaned_data['phone']
                        )
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
                            notification_type='order_update'
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

    context = {
        'cart': cart,
        'items': items,
        'form': form,
        'title': 'Cart Checkout',
        'is_cart_checkout': True
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

                    # Create order
                    order = Order.objects.create(
                        customer=request.user,
                        vendor=product.vendor,
                        total=total,
                        delivery_address=form.cleaned_data['delivery_address'],
                        phone=form.cleaned_data['phone']
                    )

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
                        notification_type='order_update'
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

    context = {
        'product': product,
        'form': form,
        'title': 'Checkout',
        'is_cart_checkout': False
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
        order.status = 'confirmed'
        order.save()
        
        # Update stock for items in this order
        for item in order.items.all():
            if item.product.stock >= item.quantity:
                item.product.stock -= item.quantity
                item.product.save()
            else:
                messages.warning(request, 
                    f"Insufficient stock for {item.product.name}. " +
                    "Please update your inventory."
                )
        
        messages.success(request, 
            f"Order #{order.id} confirmed! " +
            f"Stock has been updated and customer has been notified."
        )

        # Create notification for customer
        Notification.objects.create(
            user=order.customer,
            title="Order Confirmed",
            message=f"Your order #{order.id} has been confirmed by the vendor.",
            notification_type='order_update'
        )
        
        print(f"=== ORDER APPROVED ===")
        print(f"Order: #{order.id}")
        print(f"Vendor: {request.user.username}")
        print(f"Customer: {order.customer.username}")
        
    else:
        messages.error(request, "This order cannot be confirmed.")
    
    return redirect('vendor_orders')



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
        
        messages.success(request, f"Order #{order.id} has been cancelled.")

        # Create notification for customer
        Notification.objects.create(
            user=order.customer,
            title="Order Cancelled",
            message=f"Your order #{order.id} has been cancelled by the vendor.",
            notification_type='order_update'
        )
    else:
        messages.error(request, "This order cannot be cancelled.")
    
    return redirect('vendor_orders')

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