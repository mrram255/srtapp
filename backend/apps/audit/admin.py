from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'action',
        'module',
        'user',
        'request_method',
        'request_path',
        'response_status',
        'duration_ms',
    )
    list_filter = ('action', 'module', 'request_method', 'response_status')
    search_fields = ('request_path', 'object_repr', 'user__email')
    readonly_fields = [field.name for field in AuditLog._meta.fields]
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
