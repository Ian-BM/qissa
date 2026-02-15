from django.urls import path
from . import views
from .views import unlock_chapter

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("stories/new/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("stories/<int:story_id>/toggle/", views.story_toggle_publish, name="story_toggle_publish"),

    path("stories/<int:story_id>/chapters/", views.chapter_list, name="chapter_list"),
    path("stories/<int:story_id>/chapters/new/", views.chapter_create, name="chapter_create"),
    path("chapters/<int:chapter_id>/edit/", views.chapter_edit, name="chapter_edit"),

    path("unlock/", unlock_chapter, name="unlock_chapter"),
 
]
