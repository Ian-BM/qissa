from django.urls import path
from .views import chapter_reader, payment_page, story_detail

urlpatterns = [
    path("story/<slug:slug>/", story_detail, name="story_detail"),
    path("chapter/<int:id>/", chapter_reader, name="chapter_reader"),

    path("payment/<int:story_id>/", payment_page, name="payment_page"),

]
