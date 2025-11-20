from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, CartItem
from products.models import Product

@login_required
def view_cart(request):
    """View shopping cart"""
    cart, created = Cart.objects.get_or_create(customer=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    """Add product to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(customer=request.user)
    
    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Increase quantity if already in cart
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f"Added another {product.name} to cart")
        else:
            messages.error(request, f"Cannot add more {product.name} - limited stock")
    else:
        messages.success(request, f"Added {product.name} to cart")
    
    return redirect('view_cart')

@login_required
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated")
        elif quantity == 0:
            cart_item.delete()
            messages.success(request, "Item removed from cart")
        else:
            messages.error(request, "Invalid quantity")
    
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__customer=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart")
    return redirect('view_cart')