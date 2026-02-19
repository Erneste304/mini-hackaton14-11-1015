from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication routes
    path('register/', views.register, name='register'),


    # Custom login (handles unverified users)
    path('login/', views.login_view, name='login'),

    path('logout/', auth_views.LogoutView.as_view(
        template_name='accounts/logout.html'
    ), name='logout'),

    # Profile routes
    path('profile/', views.profile, name='profile'),

    # Notification path
    path('notifications/', views.all_notifications, name='all_notifications'),
]