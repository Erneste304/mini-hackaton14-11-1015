import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm
from .models import User
from .decorators import vendor_required, customer_required




def register(request):
    """
    Handle user registration for both vendors and customers.
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            messages.success(
                request,
                f'🎉 Account created successfully! Please verify your email to log in, {user.username}.'
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
    Custom login view: authenticate credentials, then send a 5-digit OTP.
    Actual login() happens only after OTP verification.
    """
    from django.contrib.auth import authenticate as auth_authenticate

    if request.user.is_authenticated:
        if request.user.is_vendor():
            return redirect('vendor_dashboard')
        return redirect('product_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Normal authentication
        user = auth_authenticate(request, username=username, password=password)
        if user is None:
            # check if they used email
            try:
                user_obj = User.objects.get(email=username)
                user = auth_authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            # Generate and send 5-digit OTP
            otp_code = ''.join(random.choices(string.digits, k=5))
            from .models import EmailOTP
            EmailOTP.objects.create(email=user.email, otp=otp_code)

            # Send Email
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = "Your Soko Hub Login Verification"
            
            # Generate Direct Link
            verify_url = request.build_absolute_uri(
                reverse('verify_otp_direct') + f'?email={user.email}&otp={otp_code}'
            )
            
            message = f"Hello {user.username},\n\nYour 5-digit verification code is: {otp_code}\n\nAlternatively, you can click the link below to verify and login automatically:\n{verify_url}\n\nThis code will expire in 3 minutes."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

            # Defer login: store user ID and email in session
            request.session['pending_user_id'] = user.id
            request.session['otp_email'] = user.email
            
            messages.success(request, f"A 5-digit verification code has been sent to {user.email}.")
            return redirect('verify_otp')
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


def send_otp(request):
    """Generates and sends a 5-digit OTP to the user's email."""
    if request.method == "POST":
        email = request.POST.get('email')
        if not email:
            messages.error(request, "Email is required.")
            return redirect('login')

        try:
            user = User.objects.get(email=email)
            # Generate 5-digit random OTP
            otp_code = ''.join(random.choices(string.digits, k=5))
            
            # Save OTP to database
            from .models import EmailOTP
            EmailOTP.objects.create(email=email, otp=otp_code)

            # Send Email
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = "Your Soko Hub Login OTP"
            message = f"Hello {user.username},\n\nYour 5-digit login OTP is: {otp_code}\n\nThis code will expire in 5 minutes."
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])

            request.session['otp_email'] = email
            messages.success(request, f"A 5-digit OTP has been sent to {email}.")
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, "This email is not registered.")
            return redirect('login')
    
    return render(request, 'accounts/send_otp.html', {'title': 'Send OTP - Soko Hub'})


def verify_otp(request):
    """Verifies the 5-digit OTP and finalizes user login."""
    email = request.session.get('otp_email')
    pending_user_id = request.session.get('pending_user_id')
    
    if not email and not pending_user_id:
        return redirect('login')

    if request.method == "POST":
        otp_input = request.POST.get('otp')
        from .models import EmailOTP
        
        # Verify the most recent valid OTP for this email
        otp_obj = EmailOTP.objects.filter(email=email).last()
        
        if otp_obj and otp_obj.otp == otp_input and otp_obj.is_valid():
            # If we had a pending password login, get that user
            if pending_user_id:
                user = User.objects.get(id=pending_user_id)
            else:
                # Flow from direct email-only login (if supported)
                user = User.objects.get(email=email)
                
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Cleanup session
            if 'pending_user_id' in request.session:
                del request.session['pending_user_id']
            if 'otp_email' in request.session:
                del request.session['otp_email']
                
            messages.success(request, "Login successful!")
            
            if user.is_vendor():
                return redirect('vendor_dashboard')
            return redirect('home')
        else:
            messages.error(request, "Invalid or expired verification code.")
    
    return render(request, 'accounts/verify_otp.html', {
        'title': 'Verify Login - Soko Hub',
        'email': email
    })


def verify_otp_direct(request):
    """Verifies the OTP directly from a link and finalizes login."""
    email = request.GET.get('email')
    otp = request.GET.get('otp')
    
    if not email or not otp:
        messages.error(request, "Invalid verification link.")
        return redirect('login')
        
    from .models import EmailOTP
    # Verify the most recent valid OTP for this email
    otp_obj = EmailOTP.objects.filter(email=email).last()
    
    if otp_obj and otp_obj.otp == otp and otp_obj.is_valid():
        try:
            user = User.objects.get(email=email)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Cleanup session (if any)
            if 'pending_user_id' in request.session:
                del request.session['pending_user_id']
            if 'otp_email' in request.session:
                del request.session['otp_email']
                
            messages.success(request, "Login successful via direct link!")
            
            if user.is_vendor():
                return redirect('vendor_dashboard')
            return redirect('home')
        except User.DoesNotExist:
            messages.error(request, "User associated with this link does not exist.")
            return redirect('login')
    else:
        messages.error(request, "The verification link is invalid or has expired.")
        return redirect('login')
