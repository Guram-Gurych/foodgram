from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, _, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
