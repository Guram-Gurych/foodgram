from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscription, User
from users.serializers import AvatarSerializer, SubscriptionSerializer


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
                status=status.HTTP_400_BAD_REQUEST
            )

        if Subscription.objects.filter(
            user=request.user,
            subscription=author,
        ).exists():
            return Response(
                {"detail": "Вы уже подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        Subscription.objects.create(user=request.user, subscription=author)

        serializer = SubscriptionSerializer(
            author,
            context={"request": request}
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *_, **__):
        author = self.get_author()

        subscription = Subscription.objects.filter(
            user=request.user,
            subscription=author
        )

        if not subscription.exists():
            return Response(
                {"detail": "Вы не подписаны на этого пользователя."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


subscription_list = SubscriptionViewSet.as_view({
    "get": "list"
})

subscription_detail = SubscriptionViewSet.as_view({
    "post": "create",
    "delete": "destroy"
})
