from django.contrib.auth import get_user_model
from django.db import models

from core.models import Ingredient, Tag

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    name = models.CharField(verbose_name="Название", max_length=50)
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="recipes/images/",
        null=True,
        default=None,
        blank=True,
    )
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="Ингридиент"
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Тег")
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления"
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f"{self.name} (автор: {self.author})"


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="Рецепт",
    )
    ingredients = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        return f"{self.ingredients.name} в рецепте {self.recipe.name}"


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"

    def __str__(self):
        return f"Избранное: {self.recipe.name} у {self.user}"


class ShoppingCart(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_carts",
        verbose_name="Рецепт",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart_items",
        verbose_name="Пользователь"
    )

    class Meta:
        ordering = ["recipe__name"]
        verbose_name = "Карта покупок"
        verbose_name_plural = "Карты покупок"

    def __str__(self):
        return f"{self.recipe.name} в списке у {self.user}"
