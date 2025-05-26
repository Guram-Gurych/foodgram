from django_filters import rest_framework as filters
from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    is_favorited = filters.CharFilter(method="filter_is_favorited")
    is_in_shopping_cart = filters.CharFilter(
        method="filter_is_in_shopping_cart")
    author = filters.NumberFilter(field_name="author__id")
    tags = filters.AllValuesMultipleFilter(
        field_name="tags__slug",
        distinct=True,
    )

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author", "tags")

    def filter_is_favorited(self, queryset, _, value):
        user = self.request.user

        if user.is_authenticated and value:
            return queryset.filter(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, _, value):
        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(shopping_cart__user=user).distinct()
        return queryset
