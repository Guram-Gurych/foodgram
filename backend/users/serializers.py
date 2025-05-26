from djoser.serializers import UserCreateSerializer
from rest_framework import serializers

from core.serializers import Base64ImageField, RecipeSubscriptionSerializer
from users.models import Subscription, User


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ["avatar"]


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
        user = self.context.get("request").user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, subscription=obj).exists()


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
        return Subscription.objects.filter(
            user=user, subscription=obj).exists()
