from notifications.models import Notification

def user_notifications(request):
    """Add notification data to all templates"""
    context = {}
    
    if request.user.is_authenticated:
        # Count unread notifications
        unread_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        # Get recent notifications
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        context.update({
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications,
        })
    
    return context

def vendor_notifications(request):
    """
    Context processor for vendor notifications
    """
    notifications = []
    unread_count = 0

    if request.user.is_authenticated and hasattr(request.user, 'vendor_profile'):

        pass

    return {
        'vendor_notifications': notifications,
        'vendor_unread_notifications_count': unread_count,}