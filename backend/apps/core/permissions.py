from rest_framework.permissions import BasePermission, SAFE_METHODS


def _user_role(user) -> str:
    role = getattr(user, 'role', '') or ''
    if hasattr(role, 'name'):
        return str(role.name).lower()
    return str(role).lower()


def _roles(*names: str) -> set[str]:
    return {name.lower() for name in names}


class RoleBasedPermission(BasePermission):
    """Check if user has required role for the view."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed = getattr(view, 'allowed_roles', [])
        if not allowed:
            return True

        user_role = _user_role(request.user)
        allowed_roles = _roles(*allowed)
        return user_role in allowed_roles or user_role.replace('-', '_') in allowed_roles


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or _user_role(request.user) in _roles('super_admin', 'super admin')
        )


class IsPrincipal(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles(
            'principal',
            'vice_principal',
            'director',
            'vc',
        ) or IsSuperAdmin().has_permission(request, view)


class IsRegistrar(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles('registrar', 'bursar') or IsSuperAdmin().has_permission(
            request, view
        )


class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles(
            'accountant',
            'chief_accountant',
            'cashier',
            'admin',
        ) or IsSuperAdmin().has_permission(request, view)


class IsAdmissionStaff(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles(
            'admission_officer',
            'admission_counsellor',
            'admission_staff',
        ) or IsRegistrar().has_permission(request, view) or IsSuperAdmin().has_permission(request, view)


class IsHOD(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles('hod', 'dean', 'admin') or IsSuperAdmin().has_permission(
            request, view
        )


class IsTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles('teacher', 'faculty') or IsHOD().has_permission(request, view)


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and _user_role(request.user) == 'student'


class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and _user_role(request.user) == 'parent'


class IsOwnerOrAdmin(BasePermission):
    """Object owner or elevated admin roles."""

    owner_field = 'user'

    def has_object_permission(self, request, view, obj):
        if IsSuperAdmin().has_permission(request, view):
            return True
        owner = getattr(obj, self.owner_field, None)
        if owner is None:
            owner = getattr(obj, 'created_by', None)
        return owner == request.user


class HasModulePermission(BasePermission):
    """Dynamic module-level permission check."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or IsSuperAdmin().has_permission(request, view):
            return True

        module = getattr(view, 'required_module', None)
        action = getattr(view, 'required_action', None)
        if not module or not action:
            return True

        checker = getattr(request.user, 'has_module_permission', None)
        if callable(checker):
            return bool(checker(module, action))

        if request.method in SAFE_METHODS:
            return request.user.is_staff
        return False


class HasFieldPermission(BasePermission):
    """Dynamic field-level permission check for write operations."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.is_superuser or IsSuperAdmin().has_permission(request, view):
            return True

        if request.method in SAFE_METHODS:
            return True

        module = getattr(view, 'required_module', None)
        restricted_fields = getattr(view, 'restricted_fields', [])
        if not module or not restricted_fields:
            return True

        checker = getattr(request.user, 'has_field_permission', None)
        if not callable(checker):
            return False

        payload = self._get_payload(request)
        for field in restricted_fields:
            if field in payload and not checker(module, field, 'edit'):
                return False
        return True

    @staticmethod
    def _get_payload(request):
        if hasattr(request, 'data'):
            return request.data
        if request.method in SAFE_METHODS:
            return {}
        try:
            import json

            body = getattr(request, 'body', b'') or b''
            if not body:
                return {}
            return json.loads(body.decode())
        except Exception:
            return {}


# Backward-compatible aliases used by existing modules
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles('admin') or IsSuperAdmin().has_permission(request, view)


class IsLibrarian(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return _user_role(request.user) in _roles('librarian') or IsAdmin().has_permission(request, view)
