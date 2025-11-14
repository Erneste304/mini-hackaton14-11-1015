from django.urls import path
from . import views
from django.urls import path
from . import views

urlpatterns = [
    # Public routes
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Vendor routes
    path('vendor/dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor/products/', views.vendor_products, name='vendor_products'),
    path('vendor/products/add/', views.add_product, name='add_product'),
    path('vendor/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('vendor/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
]