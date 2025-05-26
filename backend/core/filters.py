from rest_framework.filters import SearchFilter


class IngredientNameFilter(SearchFilter):
    search_param = 'name'
