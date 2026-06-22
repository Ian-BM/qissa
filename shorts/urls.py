from django.urls import path

from . import views

urlpatterns = [
    path("shorts/", views.short_list, name="short_list"),
    path("shorts/<slug:slug>/", views.short_detail, name="short_detail"),
    path("shorts/<slug:slug>/like/", views.short_like, name="short_like"),
]
