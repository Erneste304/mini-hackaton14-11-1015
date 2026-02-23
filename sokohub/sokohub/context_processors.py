from notifications.models import Notification
from cart.models import Cart

def vendor_notifications(request):
    """
    Context processor to provide unread notifications 
    and recent notifications to all templates.
    """
    if request.user.is_authenticated:
        unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]
        return {
            'unread_notifications_count': unread_notifications_count,
            'recent_notifications': recent_notifications
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }

def cart_count(request):
    """
    Context processor to provide the cart item count to all templates.
    """
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(customer=request.user)
            return {'cart_count': cart.get_items_count()}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}
