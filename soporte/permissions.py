from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    - Administrador (is_staff): Control total (lectura, escritura, borrado).
    - Usuario normal: Solo lectura y modificación de sus propias solicitudes. Prohibido DELETE.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Bloquear borrado a usuarios normales
        if request.method == 'DELETE':
            return False
        
        return obj.usuario == request.user