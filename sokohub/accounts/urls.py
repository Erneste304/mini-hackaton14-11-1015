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

    # OTP routes
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('verify-otp-direct/', views.verify_otp_direct, name='verify_otp_direct'),

    # Password Reset routes (Django built-in, no migrations needed)
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset-complete/'
         ),
         name='password_reset_confirm'),

    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # Notification path
    path('notifications/', views.all_notifications, name='all_notifications'),

    # Sokohub Card routes
    path('request-card/', views.request_sokohub_card, name='request_sokohub_card'),
    path('pay-card/', views.pay_sokohub_card, name='pay_sokohub_card'),
    path('card-details/', views.sokohub_card_details, name='sokohub_card_details'),
    path('top-up-card/', views.top_up_card, name='top_up_card'),
]