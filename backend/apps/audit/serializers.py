from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.audit.models import AuditLog

User = get_user_model()


class AuditLogListSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'action',
            'module',
            'model_name',
            'object_id',
            'object_repr',
            'ip_address',
            'request_method',
            'request_path',
            'response_status',
            'duration_ms',
            'created_at',
        ]
        read_only_fields = fields

    def get_user_email(self, obj: AuditLog) -> str | None:
        if obj.user_id:
            return obj.user.email
        return None

    def get_user_name(self, obj: AuditLog) -> str | None:
        if obj.user_id:
            return obj.user.get_full_name()
        return None


class AuditLogDetailSerializer(AuditLogListSerializer):
    class Meta(AuditLogListSerializer.Meta):
        fields = AuditLogListSerializer.Meta.fields + ['changes', 'metadata', 'user_agent', 'updated_at']
