from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (
    AvatarView,
    CustomUserViewSet,
    subscription_detail,
    subscription_list,
)

router = DefaultRouter()
router.register("", CustomUserViewSet, basename="users")

urlpatterns = [
    path("<int:pk>/subscribe/", subscription_detail),
    path("me/avatar/", AvatarView.as_view(), name="avatar"),
    path("subscriptions/", subscription_list),
    path("", include(router.urls)),
]
