from cart.models import Cart
from notifications.models import Notification

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(customer=request.user)
            return {'cart_count': cart.items.count()}
        except Cart.DoesNotExist:
            return {'cart_count': 0}
    return {'cart_count': 0}

def vendor_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        return {
            'unread_notifications_count': notifications.filter(is_read=False).count(),
            'recent_notifications': notifications.order_by('-created_at')[:5]
        }
    return {
        'unread_notifications_count': 0,
        'recent_notifications': []
    }