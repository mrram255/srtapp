from __future__ import annotations

from rest_framework import serializers

from apps.users.identity import User
from apps.users.models import Module, ModulePermission, Role, UserActivity
from apps.users.services import RoleService, UserService


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name', 'display_name', 'icon', 'parent_module', 'order']


class ModulePermissionSerializer(serializers.ModelSerializer):
    module_name = serializers.CharField(source='module.name', read_only=True)
    module_display = serializers.CharField(source='module.display_name', read_only=True)

    class Meta:
        model = ModulePermission
        fields = ['id', 'module', 'module_name', 'module_display', 'action', 'description']


class RoleListSerializer(serializers.ModelSerializer):
    user_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'display_name', 'description', 'is_system_role', 'user_count', 'created_at']


class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = ModulePermissionSerializer(many=True, read_only=True)
    permission_matrix = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id',
            'name',
            'display_name',
            'description',
            'is_system_role',
            'permissions',
            'permission_matrix',
            'created_at',
            'updated_at',
        ]

    def get_permission_matrix(self, obj):
        return RoleService.get_role_permissions_matrix(obj)


class RoleWriteSerializer(serializers.ModelSerializer):
    permissions = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True,
    )

    class Meta:
        model = Role
        fields = ['name', 'display_name', 'description', 'permissions']

    def create(self, validated_data):
        return RoleService.create_role(validated_data)

    def update(self, instance, validated_data):
        if instance.is_system_role and 'name' in validated_data:
            validated_data.pop('name')
        return RoleService.update_role(instance, validated_data)


class UserListSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    college_name = serializers.CharField(source='college.name', read_only=True, default='')

    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'email',
            'phone',
            'first_name',
            'last_name',
            'full_name',
            'role',
            'role_display',
            'college',
            'college_name',
            'is_active',
            'joined_at',
            'last_login',
        ]

    def get_role_display(self, obj):
        return obj.role_ref.display_name if obj.role_ref else obj.role


class UserDetailSerializer(serializers.ModelSerializer):
    role_display = serializers.SerializerMethodField()
    college_name = serializers.CharField(source='college.name', read_only=True, default='')
    masked_aadhaar = serializers.SerializerMethodField()
    masked_phone = serializers.SerializerMethodField()
    accessible_modules = serializers.SerializerMethodField()
    permission_matrix = serializers.SerializerMethodField()
    role_slug = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'employee_id',
            'email',
            'phone',
            'masked_phone',
            'first_name',
            'middle_name',
            'last_name',
            'full_name',
            'gender',
            'date_of_birth',
            'role',
            'role_ref',
            'role_display',
            'college',
            'college_name',
            'department',
            'profile_photo',
            'signature',
            'masked_aadhaar',
            'pan_number',
            'address_line_1',
            'address_line_2',
            'city',
            'district',
            'state',
            'pincode',
            'country',
            'is_active',
            'is_verified',
            'joined_at',
            'last_login',
            'accessible_modules',
            'permission_matrix',
            'role_slug',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['employee_id', 'joined_at', 'last_login', 'created_at', 'updated_at']

    def get_role_display(self, obj):
        return obj.role_ref.display_name if obj.role_ref else obj.role

    def get_masked_aadhaar(self, obj):
        return obj.get_masked_aadhaar()

    def get_masked_phone(self, obj):
        return obj.get_masked_phone()

    def get_accessible_modules(self, obj):
        return UserService.get_accessible_modules(obj)

    def get_role_slug(self, obj):
        return obj.role_ref.name if obj.role_ref_id else None

    def get_permission_matrix(self, obj):
        if not obj.role_ref_id:
            return []
        return RoleService.get_role_permissions_matrix(obj.role_ref)


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role_ref = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)
    role = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'email',
            'phone',
            'password',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'date_of_birth',
            'role',
            'role_ref',
            'college',
            'department',
            'aadhaar_number',
            'pan_number',
            'address_line_1',
            'address_line_2',
            'city',
            'district',
            'state',
            'pincode',
            'country',
        ]

    def create(self, validated_data):
        request = self.context.get('request')
        created_by = request.user if request and request.user.is_authenticated else None
        return UserService.create_user(validated_data, created_by=created_by)


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role_ref = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)
    role = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = [
            'phone',
            'password',
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'date_of_birth',
            'role',
            'role_ref',
            'college',
            'department',
            'profile_photo',
            'signature',
            'aadhaar_number',
            'pan_number',
            'address_line_1',
            'address_line_2',
            'city',
            'district',
            'state',
            'pincode',
            'country',
            'is_active',
            'is_verified',
        ]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        updated_by = request.user if request and request.user.is_authenticated else None
        return UserService.update_user(instance, validated_data, updated_by=updated_by)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'middle_name',
            'last_name',
            'gender',
            'date_of_birth',
            'profile_photo',
            'signature',
            'address_line_1',
            'address_line_2',
            'city',
            'district',
            'state',
            'pincode',
            'country',
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UserActivity
        fields = [
            'id',
            'user',
            'user_email',
            'action',
            'module',
            'description',
            'ip_address',
            'metadata',
            'created_at',
        ]


class BulkImportSerializer(serializers.Serializer):
    file = serializers.FileField()


class RoleCloneSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    display_name = serializers.CharField(max_length=100)
