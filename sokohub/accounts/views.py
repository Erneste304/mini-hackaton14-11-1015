import random
import string
import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserProfileForm, SokohubCardRequestForm
from .models import User, SokohubCard
from .decorators import vendor_required, customer_required
from decimal import Decimal




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
        sys.stderr.write("DEBUG: Received POST request for login\n")
        # Ensure a clean session for this new login attempt
        if 'pending_user_id' in request.session: del request.session['pending_user_id']
        if 'otp_email' in request.session: del request.session['otp_email']

        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        sys.stderr.write(f"DEBUG: Login application attempt for: {username}\n")

        # Authenticate using the custom backend (supports both username and email)
        user = auth_authenticate(request, username=username, password=password)
        sys.stderr.write(f"DEBUG: Authentication result: {user}\n")

        print(f"DEBUG: Checking if user is None: {user is None}")
        if user is None:
            print("DEBUG: User is None, checking for social account...")
            # Check if it might be a social account with no usable password
            try:
                user_obj = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
                print(f"DEBUG: Found user_obj for social check: {user_obj}")
                if not user_obj.has_usable_password():
                    print("DEBUG: User has no usable password (social account)")
                    messages.error(
                        request,
                        'This account was created via Google. Please use "Continue with Google" to sign in, '
                        'or use "Login with Email OTP" below.'
                    )
                    context = {'title': 'Login - Soko Hub'}
                    return render(request, 'accounts/login.html', context)
            except (User.DoesNotExist, User.MultipleObjectsReturned) as e:
                sys.stderr.write(f"DEBUG: Social check exception: {e}\n")
                pass

        sys.stderr.write(f"DEBUG: Final user check before redirect/error: {user}\n")
        if user is not None:
            sys.stderr.write(f"DEBUG: User is not None, is_active: {user.is_active}\n")
            if not user.is_active:
                messages.error(request, 'Your account has been disabled. Please contact support.')
                context = {'title': 'Login - Soko Hub'}
                return render(request, 'accounts/login.html', context)

            # Generate and send 5-digit OTP
            sys.stderr.write("DEBUG: Generating OTP...\n")
            otp_code = ''.join(random.choices(string.digits, k=5))
            from .models import EmailOTP
            EmailOTP.objects.create(email=user.email, otp=otp_code)

            # Send Email with direct login link
            from django.core.mail import send_mail
            from django.conf import settings

            sys.stderr.write(f"DEBUG: Sending OTP to {user.email}\n")
            subject = "Your Soko Hub Login Verification"
            verify_url = request.build_absolute_uri(
                reverse('verify_otp_direct')
            ) + f'?email={user.email}&otp={otp_code}'

            message = (
                f"Hello {user.username},\n\n"
                f"Your 5-digit verification code is: {otp_code}\n\n"
                f"Alternatively, you can click the link below to verify and login automatically:\n"
                f"{verify_url}\n\n"
                f"This code will expire in 3 minutes."
            )
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
                print("DEBUG: Email sent successfully")
            except Exception as e:
                print(f"DEBUG: Email sending failed: {e}")

            # Defer full login until OTP is verified
            request.session['pending_user_id'] = user.id
            request.session['otp_email'] = user.email

            messages.success(request, f"A verification code has been sent to {user.email}.")
            return redirect('verify_otp')
        else:
            sys.stderr.write("DEBUG: Authentication failed, adding error message\n")
            messages.error(request, 'Invalid username/email or password. Please try again.')
            context = {'title': 'Login Failed Credentials - Soko Hub'}
            return render(request, 'accounts/login.html', context)

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
        # Ensure a fresh state for OTP request
        if 'pending_user_id' in request.session: del request.session['pending_user_id']
        
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
            try:
                # If we had a pending password login, get that user
                if pending_user_id:
                    user = User.objects.get(id=pending_user_id)
                    # Safety check: ensure the email still matches the OTP email (case-insensitive)
                    if user.email.lower() != email.lower():
                        messages.error(request, "Session inconsistency. Please try logging in again.")
                        return redirect('login')
                else:
                    # Flow from direct email-only login (if supported)
                    user = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
                messages.error(request, "Account not found. Please try logging in again.")
                return redirect('login')
                
            login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            
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
            user = User.objects.get(email__iexact=email)
            login(request, user, backend='accounts.backends.EmailOrUsernameModelBackend')
            
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
        pass

@login_required
def request_sokohub_card(request):
    """View to request a Sokohub Card"""
    # Check if user already has a card
    card = SokohubCard.objects.filter(user=request.user).first()
    if card:
        if card.status == 'approved':
            return redirect('sokohub_card_details')
        return redirect('pay_sokohub_card')

    if request.method == 'POST':
        form = SokohubCardRequestForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            messages.success(request, "Card request submitted! Please proceed to payment.")
            return redirect('pay_sokohub_card')
    else:
        form = SokohubCardRequestForm(initial={'email': request.user.email, 'phone': request.user.phone})

    return render(request, 'accounts/sokohub_card_request.html', {
        'form': form,
        'title': 'Request Sokohub Card'
    })


@login_required
def pay_sokohub_card(request):
    """View to simulate payment for Sokohub Card"""
    card = get_object_or_404(SokohubCard, user=request.user)
    
    if card.status == 'approved':
        return redirect('home')

    if request.method == 'POST':
        # Simulate payment
        card.status = 'paid'
        card.is_active = True # Auto-approve for demo
        card.status = 'approved'
        card.save()

        # Generate unique card details
        card.generate_card_details()
        
        # Notify user
        from notifications.models import Notification
        # Notify user of approval
        Notification.objects.create(
            user=request.user,
            title="Sokohub Card Approved",
            message="Your Sokohub Card has been approved. You can now enjoy 5% discounts on promotion days!",
            notification_type='system'
        )

        messages.success(request, "Payment successful! Your Sokohub Card is now active.")
        return redirect('home')

    return render(request, 'accounts/sokohub_card_payment.html', {
        'card': card,
        'title': 'Pay for Sokohub Card'
    })


@login_required
def sokohub_card_details(request):
    """View to display the active Sokohub Card details"""
    card = get_object_or_404(SokohubCard, user=request.user, status='approved')
    
    return render(request, 'accounts/sokohub_card_details.html', {
        'card': card,
        'title': 'My Sokohub Card'
    })


@login_required
def top_up_card(request):
    """View to add money to Sokohub Card balance"""
    card = get_object_or_404(SokohubCard, user=request.user, status='approved')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = float(amount)
            if amount > 0:
                card.balance += Decimal(str(amount))
                card.save()
                messages.success(request, f"Successfully added ${amount:.2f} to your card balance!")
                return redirect('sokohub_card_details')
            else:
                messages.error(request, "Please enter a valid positive amount.")
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")
            
    return render(request, 'accounts/sokohub_card_topup.html', {
        'card': card,
        'title': 'Top Up Card Balance'
    })
