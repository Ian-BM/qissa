from django.urls import path
from .views import chapter_reader, payment_page, story_detail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("story/<slug:slug>/", story_detail, name="story_detail"),
    path("chapter/<int:id>/", chapter_reader, name="chapter_reader"),

    path("payment/<int:story_id>/", payment_page, name="payment_page"),
    path("login/", auth_views.LoginView.as_view(), name="login"),

]
