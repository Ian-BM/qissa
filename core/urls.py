
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.i18n import set_language

urlpatterns = [
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('admin/', admin.site.urls),
    path("set-language/", set_language, name="set_language"),
    path("", include("pages.urls")),
    path("", include("accounts.urls")),
    path("", include("stories.urls")),
    path("dashboard/", include("dashboard.urls")),
]

