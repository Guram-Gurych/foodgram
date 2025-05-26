from core.views import IngredientViewSet, TagViewSet
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="Ingredient")

urlpatterns = [
    path("", include(router.urls)),
]
