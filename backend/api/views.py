from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import generics, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientNameFilter, RecipeFilter
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (AvatarSerializer, IngredientSerializer,
                             RecipeReadSerializer,
                             RecipeSubscriptionSerializer,
                             RecipeWriteSerializer, SubscriptionSerializer,
                             TagSerializer)
from core.models import Ingredient, Tag
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart
from users.models import Subscription, User


class BaseViewSet(
    mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet
):
    model = None
    error_add = ""
    error_delete = ""

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

    def create(self, request, *_, **kwargs):
        recipe_id = kwargs.get("id")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = self.model.objects.filter(user=request.user, recipe=recipe)

        if obj.exists():
            return Response(
                {"detail": self.error_add}, status=status.HTTP_400_BAD_REQUEST
            )

        self.model.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeSubscriptionSerializer(
            recipe, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *_, **kwargs):
        recipe_id = kwargs.get("id")
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = self.model.objects.filter(user=request.user, recipe=recipe)

        if not obj.exists():
            return Response(
                {"detail": self.error_delete},
                status=status.HTTP_400_BAD_REQUEST,
            )

        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = [IngredientNameFilter]
    search_fields = ["^name"]


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-id")
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    serializer_classes = {
        "create": RecipeWriteSerializer,
        "update": RecipeWriteSerializer,
        "partial_update": RecipeWriteSerializer,
    }

    def build_response(self, instance, status_code):
        serializer = RecipeReadSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(
            serializer.data,
            status=status_code,
            headers=self.get_success_headers(serializer.data),
        )

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, RecipeReadSerializer)

    def create(self, request, *_, **__):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return self.build_response(
            serializer.instance, status.HTTP_201_CREATED)

    def partial_update(self, request, *_, **__):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.build_response(serializer.instance, status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["get"],
        url_path="get-link",
        permission_classes=[AllowAny],
    )
    def get_link(self, request, pk):
        path = reverse("recipes-detail", args=[pk])
        return Response({"short-link": request.build_absolute_uri(path)})

    @action(
        detail=False,
        methods=["get"],
        url_path="download_shopping_cart",
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user)
            .values("ingredients__name", "ingredients__measurement_unit")
            .annotate(total_amount=Sum("amount"))
        )

        text = []
        for ingredient in ingredients:
            name = ingredient["ingredients__name"]
            unit = ingredient["ingredients__measurement_unit"]
            amount = ingredient["total_amount"]
            text.append(f"{name}: {amount}{unit}")

        text_result = "\n".join(text)
        filename = "shopping_cart.txt"

        response = HttpResponse(text_result, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


class FavoriteViewSet(BaseViewSet):
    model = Favorite
    error_add = "Рецепт уже в избранном."
    error_delete = "Рецепта нет в избранном."


class ShoppingCartViewSet(BaseViewSet):
    model = ShoppingCart
    error_add = "Рецепт уже в списке покупок."
    error_delete = "Рецепта нет в списке покупок."


favorite_view = FavoriteViewSet.as_view(
    {
        "post": "create",
        "delete": "destroy",
    }
)

shopping_cart_view = ShoppingCartViewSet.as_view(
    {
        "post": "create",
        "delete": "destroy",
    }
)


class CustomUserViewSet(UserViewSet):
    def get_permissions(self):
        if self.action in ("create", "list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]


class AvatarView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = AvatarSerializer

    def get_object(self):
        return self.request.user

    def delete(self, _):
        user = self.get_object()
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(viewsets.GenericViewSet):
    serializer_class = SubscriptionSerializer

    def get_author(self):
        return get_object_or_404(User, id=self.kwargs.get("pk"))

    def get_queryset(self):
        return User.objects.filter(subscribed_to__user=self.request.user)

    def list(self, request, *_, **__):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def create(self, request, *_, **__):
        author = self.get_author()

        if request.user == author:
            return Response(
                {"detail": "Нельзя подписаться на самого себя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Subscription.objects.filter(
            user=request.user,
            subscription=author,
        ).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Subscription.objects.create(user=request.user, subscription=author)

        serializer = SubscriptionSerializer(
            author, context={"request": request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *_, **__):
        author = self.get_author()

        subscription = Subscription.objects.filter(
            user=request.user, subscription=author
        )

        if not subscription.exists():
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


subscription_list = SubscriptionViewSet.as_view({"get": "list"})

subscription_detail = SubscriptionViewSet.as_view(
    {"post": "create", "delete": "destroy"}
)
