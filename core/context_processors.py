from django.conf import settings

def admin_phones(request):
    return {
        "ADMIN_PHONES": getattr(settings, "ADMIN_PHONES", [])
    }
