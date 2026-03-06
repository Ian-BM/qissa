from functools import wraps
from django.conf import settings
from django.http import HttpResponseForbidden


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Not authenticated")

        if request.user.phone not in settings.ADMIN_PHONES:
            return HttpResponseForbidden("Admins only")

        response = view_func(request, *args, **kwargs)

        if response is None:
            return HttpResponseForbidden("Invalid response from view")

        return response

    return _wrapped_view
