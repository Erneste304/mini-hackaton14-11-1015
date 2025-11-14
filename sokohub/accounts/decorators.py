from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps
def vendor_required(view_func):
    """
    Decorator to ensure user is a vendor
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_vendor():
            return HttpResponseForbidden(
                "Access denied. Vendor account required to access this page."
            )
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped_view)

def customer_required(view_func):
    """
    Decorator to ensure user is a customer
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if not request.user.is_customer():
            return HttpResponseForbidden(
                "Access denied. Customer account required to access this page."
            )
        return view_func(request, *args, **kwargs)
    return login_required(_wrapped_view)