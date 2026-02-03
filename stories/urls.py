from django.urls import path
from .views import story_detail, chapter_reader

urlpatterns = [
    path("story/<slug:slug>/", story_detail, name="story_detail"),
    path("chapter/<int:id>/", chapter_reader, name="chapter_reader"),
]
