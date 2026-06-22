from django.contrib import admin

from .models import ShortStory, ShortStoryLike, ShortStoryView


@admin.register(ShortStory)
class ShortStoryAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "read_time",
        "views",
        "likes",
        "featured",
        "published",
        "created_at",
    )
    list_filter = ("category", "published", "featured", "created_at")
    search_fields = ("title", "content", "excerpt")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("read_time", "views", "likes", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "cover_image")}),
        ("Content", {"fields": ("content", "excerpt", "read_time")}),
        ("Status", {"fields": ("featured", "published")}),
        ("Analytics", {"fields": ("views", "likes", "created_at", "updated_at")}),
    )


@admin.register(ShortStoryLike)
class ShortStoryLikeAdmin(admin.ModelAdmin):
    list_display = ("short_story", "user", "session_key", "created_at")
    list_filter = ("created_at",)
    search_fields = ("short_story__title", "user__phone")


@admin.register(ShortStoryView)
class ShortStoryViewAdmin(admin.ModelAdmin):
    list_display = ("short_story", "user", "session_key", "viewed_at")
    list_filter = ("viewed_at",)
    search_fields = ("short_story__title", "user__phone")
