from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from core.filters import IngredientNameFilter
from core.models import Ingredient, Tag
from core.serializers import (IngredientSerializer,
                              RecipeSubscriptionSerializer, TagSerializer)
from recipes.models import Recipe


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
