from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication routes
    path('register/', views.register, name='register'),
    

    # Profile routes
    #path('profile/', views.profile, name='profile'),
    #path('profile/vendor/', views.vendor_profile, name='vendor_profile'),
    #path('profile/customer/', views.customer_profile, name='customer_profile'),

    # Django built-in auth views (with custom templates)
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='accounts/logout.html'
    ), name='logout'),


    # Use this for actual profile page
    path('profile/', views.profile, name='profile'),

    #notification path
    path('notifications/', views.all_notifications, name='all_notifications'),
]

path('debug/', views.debug_profile_pic, name='debug_pic'),