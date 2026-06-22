from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("phone", "name", "is_staff", "is_active")
    search_fields = ("phone", "name")
    list_filter = ("is_staff", "is_active")
