from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm
from .decorators import vendor_required, customer_required
from uuid import uuid4
from .forms import ProfileUpdateForm
from .models import UserProfile

def register(request):
    """
    Handle user registration for both vendors and customers
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)  # ADD request.FILES here
        if form.is_valid():
            user = form.save(commit=False)  # Don't save to database yet
            
            # Save the user first (without profile_picture)
            user.save()
            
            # Now create UserProfile with the profile picture
            profile_picture = form.cleaned_data.get('profile_picture')
            UserProfile.objects.create(
                user=user,
                profile_picture=profile_picture
            )
            
            # Log the user in after registration
            login(request, user)

            messages.success(
                request,
                f'Account created successfully! Welcome to Soko Hub, {user.username}.'
            )

            # Redirect based on user type
            if user.is_vendor():
                return redirect('vendor_dashboard')
            else:
                return redirect('product_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
        'title': 'Register - Soko Hub'
    }
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    """" User profile page"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
        
    if request.user.is_vendor():
        return redirect('vendor_dashboard')
    else:
        return redirect('customer_orders')
    # Or use this simple template approach:
    context = {
        'title': f'Profile - {request.user.username}',
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)

@vendor_required
def vendor_profile(request):
    """
    Vendor-specific profile page
    """
    context = {
        'title': 'Vendor Profile - Soko Hub'
    }
    return render(request, 'accounts/vendor_profile.html', context)

@customer_required
def customer_profile(request):
    """
    Customer-specific profile page
    """
    context = {
        'title': 'Customer Profile - Soko Hub'
    }
    return render(request, 'accounts/customer_profile.html', context)

@login_required
def profile_redirect(request):
    """
    Redirect users from /accounts/profile/ to appropriate pages
    """
    if request.user.is_vendor():
        return redirect('vendor_dashboard')
    else:
        return redirect('customer_orders')