from django.db.models import Sum
from django.http import HttpResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.permissions import IsAuthorOrReadOnly
from core.views import BaseViewSet
from recipes.filters import RecipeFilter
from recipes.models import Favorite, Recipe, RecipeIngredient, ShoppingCart
from recipes.serializers import RecipeReadSerializer, RecipeWriteSerializer


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

        text = [
            f"{ingredient['ingredients__name']}: {ingredient['total_amount']}{ingredient['ingredients__measurement_unit']}"    # noqa:E501
            for ingredient in ingredients
        ]

        text_result = "\n".join(text)

        response = HttpResponse(text_result, content_type="text/plain")
        response[
            "Content-Disposition"
        ] = 'attachment; filename="shopping_cart.txt"'

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
