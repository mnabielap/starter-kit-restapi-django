from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to admin users.
    Equivalent to auth('manageUsers') or auth('getUsers') for admins.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class IsUserOrAdmin(permissions.BasePermission):
    """
    Allows access to admins or the user themselves.
    Equivalent to logic in src/middlewares/auth.js: 
    if (req.params.userId !== user.id) ...
    """
    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.role == 'admin':
            return True
        # User can only access their own object
        return obj.id == request.user.id