from django.urls import path
from .views import story_detail, chapter_reader, payment_page

urlpatterns = [
    path("story/<slug:slug>/", story_detail, name="story_detail"),
    path("chapter/<int:id>/", chapter_reader, name="chapter_reader"),

    path("payment/<int:chapter_id>/", payment_page, name="payment_page"),

]
