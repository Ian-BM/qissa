from django.urls import path

from .views import home, premium, stories_list

urlpatterns = [
    path("", home, name="home"),
    path("simulizi-ndefu/", stories_list, name="stories_list"),
    path("premium/", premium, name="premium"),
]
