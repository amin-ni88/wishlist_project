from rest_framework import permissions

class IsWishListOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a wishlist to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user

class IsContributor(permissions.BasePermission):
    """
    Custom permission to allow contributors to view their contributions
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.contributor == request.user
        return False

class IsPublicOrOwner(permissions.BasePermission):
    """
    Custom permission to only allow access to public wishlists or to the owner
    """
    def has_object_permission(self, request, view, obj):
        if obj.is_public:
            return True
        return obj.owner == request.user
