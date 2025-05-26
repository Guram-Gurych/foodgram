from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Subscription, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "avatar",
        "is_staff",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("is_staff", "is_superuser", "is_active")
    ordering = ("username",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Аватар", {"fields": ("avatar",)}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subscription")
    search_fields = ("user__username", "subscription__username")
    list_filter = ("user", "subscription")
