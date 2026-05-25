from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ParentProfile, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'email',
        'full_name',
        'role',
        'college',
        'department',
        'is_active',
        'is_verified',
    ]
    list_filter = ['role', 'is_active', 'is_verified', 'college']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-created_at']

    fieldsets = [
        (None, {'fields': ['email', 'password']}),
        ('Personal Info', {'fields': ['first_name', 'last_name', 'phone', 'profile_photo']}),
        ('Role & Organization', {'fields': ['role', 'college', 'department']}),
        (
            'Permissions',
            {'fields': ['is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions']},
        ),
        (
            'Security',
            {
                'fields': [
                    'failed_login_attempts',
                    'locked_until',
                    'two_factor_enabled',
                    'must_change_password',
                ]
            },
        ),
        ('Soft delete', {'fields': ['is_deleted', 'deleted_at', 'deleted_by']}),
        ('Audit', {'fields': ['last_login_ip', 'last_login_device', 'created_at', 'updated_at']}),
    ]

    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': ['email', 'phone', 'first_name', 'last_name', 'role', 'password1', 'password2'],
            },
        ),
    ]

    readonly_fields = ['created_at', 'updated_at', 'last_login_ip']


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'occupation', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    filter_horizontal = ['wards']
