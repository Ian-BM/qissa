from django.contrib import admin

from .models import Chapter, Purchase, Story, StoryCategory, StoryComment


@admin.register(StoryCategory)
class StoryCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")
    search_fields = ("name",)


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "category", "views", "is_published", "created_at")
    search_fields = ("title", "category__name")
    list_filter = ("is_published", "category")


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ("title", "story", "order", "created_at")
    list_filter = ("story",)
    search_fields = ("title", "story__title")


@admin.register(StoryComment)
class StoryCommentAdmin(admin.ModelAdmin):
    list_display = ("story", "user", "created_at")
    search_fields = ("story__title", "user__phone", "user__name", "body")
    list_filter = ("story", "created_at")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = (
        "reader",
        "story",
        "amount_paid",
        "payment_reference",
        "purchased_at",
    )
    list_filter = ("purchased_at", "story")
    search_fields = ("reader__phone", "story__title", "payment_reference")
    readonly_fields = (
        "reader",
        "story",
        "amount_paid",
        "payment_reference",
        "purchased_at",
    )

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
