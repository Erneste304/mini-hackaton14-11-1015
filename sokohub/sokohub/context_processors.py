from orders.models import OrderItem

def vendor_notifications(request):
    """Add vendor notification data to all templates"""
    context = {'pending_orders_count': 0}
    
    try:
        # Only process if user is authenticated and is a vendor
        if request.user.is_authenticated and hasattr(request.user, 'is_vendor') and request.user.is_vendor():
            pending_orders_count = OrderItem.objects.filter(
                product__vendor=request.user,
                order__status='pending' 
            ).count()
            
            context['pending_orders_count'] = pending_orders_count
            
            print(f"=== NOTIFICATIONS ===")
            print(f"Vendor: {request.user.username}")
            print(f"Pending orders: {pending_orders_count}")
            
    except Exception as e:
        print(f"Notification context error: {e}")
        context['pending_orders_count'] = 0
    
    return context