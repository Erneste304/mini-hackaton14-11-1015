from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Notification

@login_required
def mark_notification_read(request, notification_id):
    """Marks a notification as read and redirects back to the previous page or dashboard."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    
    # Redirect to target_url if present, otherwise follow next param or default
    if notification.target_url:
        return redirect(notification.target_url)
    
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    
    if request.user.user_type == 'vendor':
        return redirect('vendor_dashboard')
    return redirect('customer_orders')
