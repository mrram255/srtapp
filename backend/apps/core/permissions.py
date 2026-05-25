from rest_framework.permissions import BasePermission


class RoleBasedPermission(BasePermission):
    """
    Check if user has required role for the view.
    Set allowed_roles on the view class.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed = getattr(view, 'allowed_roles', [])
        if not allowed:
            return True

        return request.user.role in allowed


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'SUPER_ADMIN'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'ADMIN']


class IsHOD(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['SUPER_ADMIN', 'ADMIN', 'HOD']


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER']
        )


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'STUDENT'


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'PARENT'


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['SUPER_ADMIN', 'ADMIN', 'ACCOUNTANT']
        )


class IsLibrarian(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['SUPER_ADMIN', 'ADMIN', 'LIBRARIAN']
        )
