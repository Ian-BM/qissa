from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("stories/", views.story_list, name="story_list"),
    path("stories/new/", views.story_create, name="story_create"),
    path("stories/<int:story_id>/edit/", views.story_edit, name="story_edit"),
    path("stories/<int:story_id>/manage/", views.story_manage, name="story_manage"),
    path("stories/<int:story_id>/price/", views.story_update_price, name="story_update_price"),
    path(
        "stories/<int:story_id>/toggle/",
        views.story_toggle_publish,
        name="story_toggle_publish",
    ),
    path("stories/<int:story_id>/chapters/", views.chapter_list, name="chapter_list"),
    path(
        "stories/<int:story_id>/chapters/new/",
        views.chapter_create,
        name="chapter_create",
    ),
    path(
        "stories/<int:story_id>/chapters/bulk/",
        views.chapter_bulk_lock,
        name="chapter_bulk_lock",
    ),
    path("chapters/<int:chapter_id>/edit/", views.chapter_edit, name="chapter_edit"),
    path(
        "chapters/<int:chapter_id>/toggle-lock/",
        views.chapter_toggle_lock,
        name="chapter_toggle_lock",
    ),
    path("monetization/", views.monetization_overview, name="dashboard_monetization"),
    path("performance/", views.performance_overview, name="dashboard_performance"),
    path("shorts/", views.shorts_overview, name="dashboard_shorts"),
    path("shorts/new/", views.short_create, name="short_create"),
    path("shorts/<int:short_id>/edit/", views.short_edit, name="short_edit"),
    path(
        "shorts/<int:short_id>/toggle/",
        views.short_toggle_publish,
        name="short_toggle_publish",
    ),
    path("shorts/<int:short_id>/delete/", views.short_delete, name="short_delete"),
    path("stories/<int:story_id>/delete/", views.story_delete, name="story_delete"),
    path("drafts/", views.drafts_overview, name="dashboard_drafts"),
    path("unlock/", views.unlock_chapter, name="unlock_chapter"),
    path(
        "unlock/<int:story_id>/toggle/<int:user_id>/",
        views.toggle_story_access,
        name="toggle_story_access",
    ),
]
