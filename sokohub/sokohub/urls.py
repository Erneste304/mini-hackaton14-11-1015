from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    path('cart/', include('cart.urls')),
    path('notifications/', include('notifications.urls')),

    # social auth
    path('accounts/', include('allauth.urls')),
    
    # Top-level logout fallback (safe to have)
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
