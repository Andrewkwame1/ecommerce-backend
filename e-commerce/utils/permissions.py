from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdminUser(BasePermission):
    """Permission for admin users only"""
    message = 'Admin access required.'
    
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)


class IsOwner(BasePermission):
    """Permission for object owner"""
    message = 'You do not own this object.'
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAuthenticatedReadOnly(BasePermission):
    """Read-only permission for authenticated users"""
    
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return bool(request.user and request.user.is_authenticated)
