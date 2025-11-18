from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from accounts.decorators import customer_required, vendor_required
from products.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm

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
                    quantity = form.cleaned_data['quantity']

                    # Check stock availability again (prevent race condition)
                    if product.stock < quantity:
                        messages.error(request, f'Sorry, only {product.stock} items available in stock.')
                        return redirect('checkout', product_id=product_id)

                    # Calculate total
                    total = product.price * quantity

                    # Create order
                    order = Order.objects.create(
                        customer=request.user,
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

                    messages.success(request, f'Order placed successfully! Your order number is #{order.id}')
                    return redirect('order_confirmation', order_id=order.id)

            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
                # You might want to log this error in production

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
        'title': 'Checkout'
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
    """Vendor's order management"""
    order_items = OrderItem.objects.filter(product__vendor=request.user).select_related('order', 'product').order_by('-created_at')
    return render(request, 'orders/vendor_orders.html', {'order_items': order_items})
@vendor_required
def approve_order(request, order_id):
    """"Approve an order"""
    order = get_object_or_404(Order, id=order_id)
    
    # check if order contain vendor products
    vendor_items = order.items.filter(product__vendor=request.user)
    if not vendor_items.exists():
        messages.error(request, 'You can only approve orders containing your products.')
        return redirect('vendor_orders')

    if order.can_be_confirmed():
        order.status = 'confirmed'
        order.save()
        messages.success(request, f"Order #{order.id} confirmed successfully!")
    else:
        messages.error(request, "This order cannot be confirmed.")

    return redirect('vendor_orders')

@vendor_required
def cancel_order(request, order_id):
    """Vendor cancels an order"""
    order = get_object_or_404(Order, id=order_id)

    vendor_items = order.items.filter(product__vendor=request.user)
    if not vendor_items.exists():
        messages.error(request, "You can only cancel orders containing your products.")
        return redirect('vendor_orders')

    if order.can_be_cancelled():
        order.status = 'cancelled'

        # Restore stock
        for item in vendor_items:
            item.product.stock += item.quantity
            item.product.save()

        order.save()
        messages.success(request, f"Order #{order.id} cancelled.")
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