from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from accounts.decorators import vendor_required
from .models import Product, Category, ProductImage
from .forms import ProductForm
from django.db.models import Count, Sum
from orders.models import OrderItem


def home(request):
    """Homepage view with features and categories"""
    featured_products = Product.objects.filter(status='active').select_related('category').order_by('-created_at')[:8]
    trending_products = Product.objects.filter(status='active', is_trending=True).select_related('category').order_by('-created_at')[:8]
    categories = Category.objects.annotate(product_count=Count('products')).filter(product_count__gt=0)[:4]
    
    # Fallback categories if none have products yet
    if not categories.exists():
        categories = Category.objects.all()[:4]

    context = {
        'featured_products': featured_products,
        'trending_products': trending_products,
        'categories': categories,
        'title': 'Soko Hub - Online Marketplace'
    }
    return render(request, 'products/home.html', context)


def about(request):
    """About page view"""
    return render(request, 'products/about.html', {'title': 'About Soko Hub'})


def contact(request):
    """Contact page view"""
    return render(request, 'products/contact.html', {'title': 'Contact Us'})


def product_list(request, category_slug=None):
    """Browse products with filtering and sorting"""
    category = None
    categories = Category.objects.annotate(product_count=Count('products'))
    products_list = Product.objects.filter(status='active')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products_list = products_list.filter(category=category)

    search_query = request.GET.get('search', '')
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(vendor__username__icontains=search_query)
        )

    # Filtering by Price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products_list = products_list.filter(price__gte=min_price)
    if max_price:
        products_list = products_list.filter(price__lte=max_price)

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        products_list = products_list.order_by('price')
    elif sort == 'price_high':
        products_list = products_list.order_by('-price')
    elif sort == 'name':
        products_list = products_list.order_by('name')
    else:
        products_list = products_list.order_by('-created_at')

    # Pagination
    paginator = Paginator(products_list, 12)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'title': category.name if category else 'All Products',
        'search_query': search_query,
        'sort': sort,
        'min_price': min_price,
        'max_price': max_price,
        'total_products': products_list.count()
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    """Product detail page"""
    # Allow both active and out_of_stock products to be viewed
    product = get_object_or_404(Product, Q(id=product_id) & (Q(status='active') | Q(status='out_of_stock')))
    related_products = Product.objects.filter(
        category=product.category,
        status='active'
    ).exclude(id=product.id).order_by('-created_at')[:4]

    if not related_products.exists():
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

@vendor_required
def vendor_dashboard(request):
    products = Product.objects.filter(vendor=request.user)
    active_products = products.filter(status='active')
    out_of_stock_products = products.filter(status='out_of_stock')

    total_inventory_value = sum(product.price * product.stock for product in active_products)
    recent_products = products.order_by('-created_at')[:5]

    context = {
        'total_products': products.count(),
        'active_products': active_products.count(),
        'out_of_stock_products': out_of_stock_products.count(),
        'total_inventory_value': total_inventory_value,
        'recent_products': recent_products,
        'title': 'Vendor Dashboard',
        
        # Simulated RRA Compliance Data
        'rra_compliance': {
            'has_tin': bool(request.user.tin_number),
            'tin': request.user.tin_number,
            'status': 'Compliant' if request.user.tin_number else 'Incomplete',
            'penalty_alert': True if not request.user.tin_number else False,
            'message': "Please add your TIN number to avoid RRA penalties." if not request.user.tin_number else "Your tax declarations are up to date."
        }
    }
    return render(request, 'products/vendor_dashboard.html', context)

@vendor_required
def vendor_products(request):
    products = Product.objects.filter(vendor=request.user).order_by('-created_at')
    context = {
        'products': products,
        'title': 'My Products'
    }
    return render(request, 'products/vendor_products.html', context)

@vendor_required
def add_product(request):
    """Add new product with category selection"""
    categories = Category.objects.all()
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price = request.POST.get('price')
            stock = request.POST.get('stock')
            status = request.POST.get('status', 'active')
            category_id = request.POST.get('category')
            image = request.FILES.get('image')

            if not name or not price or not stock:
                messages.error(request, 'Please fill all required fields.')
                return render(request, 'products/add_product.html', {'categories': categories})

            product = Product(
                vendor=request.user,
                name=name,
                description=description or '',
                price=float(price),
                stock=int(stock),
                status=status
            )
            
            if category_id:
                product.category = Category.objects.get(id=category_id)

            if image:
                product.image = image

            product.save()

            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)

            messages.success(request, f'Product "{name}" added successfully!')
            return redirect('vendor_products')

        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')

    return render(request, 'products/add_product.html', {'categories': categories, 'title': 'Add Product'})

@vendor_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            for img in images:
                ProductImage.objects.create(product=product, image=img)
                
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


def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, 'products/privacy_policy.html', {'title': 'Privacy Policy - Soko Hub'})


def terms_of_service(request):
    """Terms of Service page view"""
    return render(request, 'products/terms_of_service.html', {'title': 'Terms of Service - Soko Hub'})


def help_center(request):
    """Help Center page view"""
    return render(request, 'products/help_center.html', {'title': 'Help Center - Soko Hub'})
