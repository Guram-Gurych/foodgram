import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated

from api.mixins import ImageMixin
from core.constants import MIN_VALUE_MODEL, MAX_VALUE_MODEL
from core.models import Ingredient, Tag
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart
from users.models import Subscription, User


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class IngredientInRecipeSerializer(serializers.Serializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        min_value=MIN_VALUE_MODEL,
        max_value=MAX_VALUE_MODEL
    )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="ingredients.id")
    name = serializers.ReadOnlyField(source="ingredients.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredients.measurement_unit",
    )

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "image",
            "cooking_time",
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ["avatar"]


class UserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name", "password")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class UserSerializer(UserCreateSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ("is_subscribed", "avatar")

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj.subscribed_to.filter(user=user).exists()


class SubscriptionSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
            "recipes",
            "recipes_count",
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=["user", "subscription"],
            )
        ]

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        if limit:
            limit = int(limit)

        queryset = obj.recipes.all()[:limit]

        return RecipeSubscriptionSerializer(
            queryset, many=True, context=self.context
        ).data

    def get_is_subscribed(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj.subscribed_to.filter(user=user).exists()


class RecipeWriteSerializer(serializers.ModelSerializer, ImageMixin):
    ingredients = IngredientInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    cooking_time = serializers.IntegerField(
        min_value=MIN_VALUE_MODEL,
        max_value=MAX_VALUE_MODEL)
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
        recipe.recipe_ingredients.all().delete()
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
                    {"ingredients": "The list of ingredients cannot be empty."}
                )

            vaild_ingredients = {}
            for item in ingredients:
                ingredient = item["id"]
                if ingredient in vaild_ingredients:
                    raise serializers.ValidationError(
                        {"ingredients": "Ingredients should not be repeated."}
                    )
                vaild_ingredients[ingredient] = True

        tags = data.get("tags")
        if tags is not None:
            if not tags:
                raise serializers.ValidationError(
                    {"tags": "The list of tags cannot be empty."}
                )

            valid_tags = {}
            for tag in tags:
                if tag in valid_tags:
                    raise serializers.ValidationError(
                        {"tags": "Tags should not be repeated."}
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
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.favorited_by.filter(user=user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_authenticated:
            return obj.in_shopping_carts.filter(user=user).exists()
        return False
