from django.urls import include, path
from rest_framework import routers

from api.views import RecipeViewSet, favorite_view, shopping_cart_view

router = routers.DefaultRouter()
router.register("", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("<int:id>/favorite/", favorite_view, name="favorite"),
    path("<int:id>/shopping_cart/", shopping_cart_view, name="shopping_cart"),
]
