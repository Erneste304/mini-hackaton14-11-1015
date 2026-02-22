from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm
from .models import User
from .decorators import vendor_required, customer_required




def register(request):
    """
    Handle user registration for both vendors and customers.
    After saving, user is set inactive until OTP is verified.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            messages.success(
                request,
                f'🎉 Account created successfully! You can now log in, {user.username}.'
            )
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'title': 'Register - Soko Hub'
    }
    return render(request, 'accounts/register.html', context)




def login_view(request):
    """
    Custom login view: after Django authenticates, check email_verified.
    Unverified users are sent to the OTP page.
    """
    from django.contrib.auth import authenticate as auth_authenticate

    if request.user.is_authenticated:
        if request.user.is_vendor():
            return redirect('vendor_dashboard')
        return redirect('product_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Try to find and authenticate user (even if inactive to check email)
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            try:
                user_obj = User.objects.get(email=username)
            except User.DoesNotExist:
                user_obj = None

        # Normal authentication
        user = auth_authenticate(request, username=username, password=password)
        if user is None and user_obj:
            # maybe they used email as username field
            user = auth_authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            if user.is_vendor():
                return redirect('vendor_dashboard')
            return redirect('product_list')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    context = {'title': 'Login - Soko Hub'}
    return render(request, 'accounts/login.html', context)


@login_required
def profile(request):
    """User profile view and update"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'title': 'My Profile - Soko Hub'
    }
    return render(request, 'accounts/profile.html', context)


@vendor_required
def vendor_profile(request):
    context = {'title': 'Vendor Profile - Soko Hub'}
    return render(request, 'accounts/vendor_profile.html', context)


@customer_required
def customer_profile(request):
    context = {'title': 'Customer Profile - Soko Hub'}
    return render(request, 'accounts/customer_profile.html', context)


@login_required
def profile_redirect(request):
    if request.user.is_vendor():
        return redirect('vendor_dashboard')
    else:
        return redirect('customer_orders')


@login_required
def all_notifications(request):
    from notifications.models import Notification
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/notifications.html', {
        'title': 'My Notifications - Soko Hub',
        'recent_notifications': notifs
    })
