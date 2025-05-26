from core.models import Tag
from core.serializers import (Base64ImageField, IngredientInRecipeSerializer,
                              TagSerializer)
from recipes.mixins import ImageMixin
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated
from users.serializers import UserSerializer


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeWriteSerializer(serializers.ModelSerializer, ImageMixin):
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    cooking_time = serializers.IntegerField(min_value=1)
    image = Base64ImageField(allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "image",
            "author",
            "tags",
            "image_url",
            "ingredients",
            "cooking_time",
        )
        read_only_fields = ("id", "author")

    def _save_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredients=item["id"],
                    amount=item["amount"],
                )
                for item in ingredients
            ]
        )

    def validate(self, data):
        if (
            "ingredients" not in self.initial_data
            or "tags" not in self.initial_data
        ):
            raise serializers.ValidationError({
                "ingredients": (
                    "This field is required for partial update."
                )
            })

        ingredients = data.get("ingredients")
        if ingredients is not None:
            if not ingredients:
                raise serializers.ValidationError(
                    {"ingredients": "Список ингредиентов не может быть пустым."}
                )

            vaild_ingredients = {}
            for item in ingredients:
                ingredient = item["id"]
                if ingredient in vaild_ingredients:
                    raise serializers.ValidationError(
                        {"ingredients": "Ингредиенты не должны повторяться."}
                    )
                vaild_ingredients[ingredient] = True

        tags = data.get("tags")
        if tags is not None:
            if not tags:
                raise serializers.ValidationError(
                    {"tags": "Список тегов не может быть пустым."}
                )

            valid_tags = {}
            for tag in tags:
                if tag in valid_tags:
                    raise serializers.ValidationError(
                        {"tags": "Теги не должны повторяться."}
                    )
                valid_tags[tag] = True

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        validated_data["author"] = self.context["request"].user

        if request.user.is_authenticated:
            recipe = Recipe.objects.create(**validated_data)
            recipe.tags.set(tags)

            self._save_ingredients(recipe, ingredients)

            return recipe
        raise NotAuthenticated("Authentication credentials were not provided.")

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients", None)
        tags = validated_data.pop("tags", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if tags is not None:
            instance.tags.set(tags)

        if ingredients is not None:
            self._save_ingredients(instance, ingredients)

        instance.save()
        return instance


class RecipeReadSerializer(serializers.ModelSerializer, ImageMixin):
    ingredients = RecipeIngredientSerializer(
        many=True,
        source="recipe_ingredients",
    )
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(min_value=1)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "text",
            "image",
            "tags",
            "ingredients",
            "author",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        return False
