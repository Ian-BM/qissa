from django.urls import path
from .views import chapter_reader, payment_page, story_detail, story_react
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("story/<slug:slug>/", story_detail, name="story_detail"),
    path("story/<slug:slug>/react/", story_react, name="story_react"),
    path("chapter/<int:id>/", chapter_reader, name="chapter_reader"),

    path("payment/<int:story_id>/", payment_page, name="payment_page"),
    path("login/", auth_views.LoginView.as_view(), name="login"),

]
