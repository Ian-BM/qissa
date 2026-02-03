from django.conf import settings
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("/login/")
        if request.user.phone not in settings.ADMIN_PHONES:
            raise PermissionDenied("Admins only")
        return view_func(request, *args, **kwargs)
    return wrapper
