from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import vendor_required
from .models import Product
from .forms import ProductForm
from django.db.models import Count, Sum
from orders.models import OrderItem

# Add the missing home view
def home(request):
    """Homepage with featured products"""
    featured_products = Product.objects.filter(status='active').order_by('-created_at')[:8]

    context = {
        'featured_products': featured_products,
        'title': 'Soko Hub - Online Marketplace'
    }
    return render(request, 'products/home.html', context)

# Add other essential views that might be missing
def product_list(request):
    """Browse all active products"""
    products_list = Product.objects.filter(status='active').order_by('-created_at')

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor__username__icontains=search_query)
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products_list = products_list.order_by('price')
    elif sort == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort == 'name':
        products_list = products_list.order_by('name')

    # Pagination
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'products': products,
        'title': 'All Products',
        'search_query': search_query,
        'sort': sort,
        'total_products': products_list.count()
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    """Product detail page"""
    try:
        product = get_object_or_404(Product, id=product_id, status='active')

        # Get related products from the same vendor
        related_products = Product.objects.filter(
            vendor=product.vendor,
            status='active'
        ).exclude(id=product.id).order_by('-created_at')[:4]

        context = {
            'product': product,
            'related_products': related_products,
            'title': product.name
        }
        return render(request, 'products/product_detail.html', context)

    except Product.DoesNotExist:
        raise Http404("Product does not exist")

@vendor_required
def vendor_dashboard(request):
    products = Product.objects.filter(vendor=request.user)
    active_products = products.filter(status='active')
    out_of_stock_products = products.filter(status='out_of_stock')

    # Calculate total value of inventory
    total_inventory_value = sum(product.price * product.stock for product in active_products)
    recent_products = products.order_by('-created_at')[:5]

    context = {
        'total_products': products.count(),
        'active_products': active_products.count(),
        'out_of_stock_products': out_of_stock_products.count(),
        'total_inventory_value': total_inventory_value,
        'recent_products': recent_products,
        'title': 'Vendor Dashboard'
    }
    return render(request, 'products/vendor_dashboard.html', context)


@vendor_required
def vendor_products(request):
    """Vendor's product management page - SIMPLE VERSION"""
    # Get all products for this vendor
    products = Product.objects.filter(vendor=request.user).order_by('-created_at')

    context = {
        'products': products,
        'title': 'My Products'
    }
    return render(request, 'products/vendor_products.html', context)
@vendor_required
def add_product(request):
    """Add new product with image upload"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            image = request.FILES.get('image')

            # Validation
            if not name or not price or not stock:
                messages.error(request, 'Please fill all required fields.')
                return render(request, 'products/add_product.html')

            # Create product
            product = Product(
                vendor=request.user,
                name=name,
                description=description or '',
                price=float(price),
                stock=int(stock)
            )

            # Handle image upload
            if image:
                product.image = image

            product.save()
            messages.success(request, f'Product "{name}" added successfully!')
            return redirect('vendor_products')

        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')

    return render(request, 'products/add_product.html')

@vendor_required
def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id, vendor=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('vendor_products')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'title': f'Edit {product.name}'
    }
    return render(request, 'products/edit_product.html', context)