from django.contrib import admin

from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart

admin.site.empty_value_display = "Не задано"


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "name", "text", "author", "get_tags", "get_ingredients")
    search_fields = ("name", "author__username")
    list_filter = ("tags",)
    inlines = [RecipeIngredientInline]

    def get_tags(self, obj):
        return ", ".join(i.name for i in obj.tags.all())

    get_tags.short_description = "Теги"

    def get_ingredients(self, obj):
        return ", ".join(i.name for i in obj.ingredients.all())

    get_ingredients.short_description = "Ингредиенты"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ("id", "recipe", "ingredients", "amount")
    list_filter = ("ingredients",)
    search_fields = ("recipe__name", "ingredients__name")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user__username", "recipe__name")
    list_filter = ("user",)
