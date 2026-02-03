from django.contrib import admin
from .models import Story, Chapter


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "views", "is_published", "created_at")
    search_fields = ("title",)
    list_filter = ("is_published",)


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "story", "order", "created_at")
    list_filter = ("story",)
    search_fields = ("title", "story__title")
