from __future__ import annotations

import io

import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.http import HttpResponse
from openpyxl import Workbook
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView

from apps.authentication.services import AuthService
from apps.core.permissions import HasModulePermission
from apps.core.responses import APIResponse
from apps.users.models import Module, ModulePermission, Role, UserActivity
from apps.users.serializers import (
    BulkImportSerializer,
    ModulePermissionSerializer,
    ModuleSerializer,
    ProfileUpdateSerializer,
    RoleCloneSerializer,
    RoleDetailSerializer,
    RoleListSerializer,
    RoleWriteSerializer,
    UserActivitySerializer,
    UserCreateSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)
from apps.users.services import RoleService, UserService

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    role = django_filters.CharFilter(field_name='role')
    role_ref = django_filters.NumberFilter(field_name='role_ref_id')
    college = django_filters.UUIDFilter(field_name='college_id')
    department = django_filters.UUIDFilter(field_name='department_id')
    is_active = django_filters.BooleanFilter(field_name='is_active')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = User
        fields = ['role', 'role_ref', 'college', 'department', 'is_active']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value)
            | Q(last_name__icontains=value)
            | Q(email__icontains=value)
            | Q(phone__icontains=value)
            | Q(employee_id__icontains=value)
        )


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.filter(is_deleted=False).select_related('college', 'department', 'role_ref')
    filterset_class = UserFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'employee_id']
    ordering_fields = ['created_at', 'joined_at', 'email', 'first_name']
    ordering = ['-created_at']
    required_module = 'users'

    def get_permissions(self):
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'activity': 'view',
            'export': 'export',
            'import_template': 'export',
            'create': 'create',
            'bulk_create': 'import',
            'update': 'edit',
            'partial_update': 'edit',
            'reset_password': 'edit',
            'toggle_2fa': 'edit',
            'change_role': 'edit',
            'bulk_activate': 'edit',
            'bulk_deactivate': 'edit',
            'destroy': 'delete',
        }
        self.required_action = action_map.get(self.action, 'view')
        return [IsAuthenticated(), HasModulePermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in {'update', 'partial_update'}:
            return UserUpdateSerializer
        return UserDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, UserListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        return APIResponse.success(UserDetailSerializer(user, context={'request': request}).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        user = serializer.save()
        return APIResponse.success(
            UserDetailSerializer(user, context={'request': request}).data,
            message='User created.',
            status=201,
        )

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=kwargs.get('partial', False), context={'request': request})
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        user = serializer.save()
        return APIResponse.success(UserDetailSerializer(user, context={'request': request}).data, message='User updated.')

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.soft_delete(user=request.user)
        UserService.log_activity(request.user, 'delete', module='users', description=f'Deleted user {user.email}', request=request)
        return APIResponse.success(message='User deactivated.')

    @action(detail=False, methods=['post'], url_path='bulk-create', parser_classes=[MultiPartParser, FormParser])
    def bulk_create(self, request):
        serializer = BulkImportSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        try:
            result = UserService.bulk_import_users(serializer.validated_data['file'], created_by=request.user)
        except ValueError as exc:
            return APIResponse.error(message=str(exc), status=400)
        return APIResponse.success(result, message='Bulk import completed.')

    @action(detail=False, methods=['post'], url_path='bulk-activate')
    def bulk_activate(self, request):
        ids = request.data.get('user_ids', [])
        updated = User.objects.filter(id__in=ids, is_deleted=False).update(is_active=True)
        return APIResponse.success({'updated': updated}, message='Users activated.')

    @action(detail=False, methods=['post'], url_path='bulk-deactivate')
    def bulk_deactivate(self, request):
        ids = request.data.get('user_ids', [])
        count = 0
        for user in User.objects.filter(id__in=ids, is_deleted=False):
            UserService.deactivate_user(user, deactivated_by=request.user)
            count += 1
        return APIResponse.success({'updated': count}, message='Users deactivated.')

    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        user = self.get_object()
        activities = UserActivity.objects.filter(user=user).order_by('-created_at')[:100]
        return APIResponse.success(UserActivitySerializer(activities, many=True).data)

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        user = self.get_object()
        password = request.data.get('password') or 'ChangeMe@123'
        user.set_password(password)
        user.must_change_password = True
        user.save(update_fields=['password', 'must_change_password', 'password_changed_at', 'updated_at'])
        UserService.log_activity(request.user, 'update', module='users', description=f'Reset password for {user.email}', request=request)
        return APIResponse.success(message='Password reset successfully.')

    @action(detail=True, methods=['post'], url_path='toggle-2fa')
    def toggle_2fa(self, request, pk=None):
        user = self.get_object()
        user.two_factor_enabled = not user.two_factor_enabled
        user.save(update_fields=['two_factor_enabled', 'updated_at'])
        return APIResponse.success({'two_factor_enabled': user.two_factor_enabled}, message='2FA toggled.')

    @action(detail=True, methods=['post'], url_path='change-role')
    def change_role(self, request, pk=None):
        user = self.get_object()
        role_id = request.data.get('role_id')
        if not role_id:
            return APIResponse.error(message='role_id is required.', status=400)
        role = Role.objects.filter(pk=role_id).first()
        if not role:
            return APIResponse.error(message='Role not found.', status=404)
        user.role_ref = role
        user.role = role.name.upper()
        user.save(update_fields=['role_ref', 'role', 'updated_at'])
        UserService.log_activity(request.user, 'update', module='users', description=f'Changed role for {user.email}', request=request)
        return APIResponse.success(UserDetailSerializer(user, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        content = UserService.export_users(queryset)
        response = HttpResponse(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="users.xlsx"'
        return response

    @action(detail=False, methods=['get'], url_path='import-template')
    def import_template(self, request):
        wb = Workbook()
        ws = wb.active
        ws.append(['email', 'phone', 'first_name', 'last_name', 'role', 'password'])
        ws.append(['user@example.com', '+919876543210', 'John', 'Doe', 'teacher', 'ChangeMe@123'])
        buffer = io.BytesIO()
        wb.save(buffer)
        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="user_import_template.xlsx"'
        return response


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.annotate(user_count=Count('users')).order_by('display_name')
    required_module = 'users'

    def get_permissions(self):
        self.required_action = 'view' if self.action in {'list', 'retrieve', 'users', 'permissions'} else 'edit'
        if self.action == 'create':
            self.required_action = 'create'
        if self.action == 'destroy':
            self.required_action = 'delete'
        return [IsAuthenticated(), HasModulePermission()]

    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return RoleWriteSerializer
        return RoleDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, RoleListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        role = self.get_object()
        return APIResponse.success(RoleDetailSerializer(role).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        role = serializer.save()
        return APIResponse.success(RoleDetailSerializer(role).data, message='Role created.', status=201)

    def update(self, request, *args, **kwargs):
        role = self.get_object()
        serializer = self.get_serializer(role, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        role = serializer.save()
        return APIResponse.success(RoleDetailSerializer(role).data, message='Role updated.')

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()
        if role.is_system_role:
            return APIResponse.error(message='System roles cannot be deleted.', status=403)
        if role.users.exists():
            return APIResponse.error(message='Role is assigned to users.', status=400)
        role.delete()
        return APIResponse.success(message='Role deleted.')

    @action(detail=True, methods=['post', 'get'])
    def permissions(self, request, pk=None):
        role = self.get_object()
        if request.method == 'GET':
            return APIResponse.success(RoleService.get_role_permissions_matrix(role))
        permission_ids = request.data.get('permissions', [])
        RoleService.set_permissions(role, permission_ids)
        return APIResponse.success(RoleDetailSerializer(role).data, message='Permissions updated.')

    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        role = self.get_object()
        users = User.objects.filter(role_ref=role, is_deleted=False)
        return APIResponse.paginated(users, UserListSerializer, request)

    @action(detail=True, methods=['post'])
    def clone(self, request, pk=None):
        role = self.get_object()
        serializer = RoleCloneSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        clone = RoleService.clone_role(role, serializer.validated_data['name'], serializer.validated_data['display_name'])
        return APIResponse.success(RoleDetailSerializer(clone).data, message='Role cloned.', status=201)


class ModuleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Module.objects.filter(parent_module__isnull=True).prefetch_related('children', 'permissions')
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        modules = self.get_queryset()
        data = []
        for module in modules:
            item = ModuleSerializer(module).data
            item['children'] = ModuleSerializer(module.children.all(), many=True).data
            data.append(item)
        return APIResponse.success(data)

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        module = self.get_object()
        perms = ModulePermission.objects.filter(module=module)
        return APIResponse.success(ModulePermissionSerializer(perms, many=True).data)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return APIResponse.success(UserDetailSerializer(request.user, context={'request': request}).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        serializer.save()
        UserService.log_activity(request.user, 'update', module='profile', description='Updated profile', request=request)
        return APIResponse.success(UserDetailSerializer(request.user, context={'request': request}).data)


class ProfilePhotoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        photo = request.data.get('photo') or request.data.get('file')
        if not photo:
            return APIResponse.error(message='Photo file is required.', status=400)
        request.user.profile_photo = getattr(photo, 'name', str(photo))
        request.user.save(update_fields=['profile_photo', 'updated_at'])
        return APIResponse.success({'profile_photo': request.user.profile_photo}, message='Photo updated.')
