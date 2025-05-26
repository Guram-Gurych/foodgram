from django.contrib import admin

from core.models import Ingredient, Tag

admin.site.empty_value_display = "Не задано"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "measurement_unit")
    list_filter = ("measurement_unit",)
    search_fields = ("name",)
    ordering = ("name",)
