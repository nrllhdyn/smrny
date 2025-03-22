from rest_framework import permissions

class IsAuthenticatedReadCreateOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return request.method == 'GET' and view.action == 'list'
        
        if request.method in ['GET', 'POST']:
            return True
            
        if request.user.is_staff:
            return True
            
        return False

class IsAdminUserForHighPriceDelete(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
            
        if obj.price > 50 and not request.user.is_staff:
            return False
            
        return True