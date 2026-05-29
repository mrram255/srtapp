from __future__ import annotations

from django.db.models import Count
from django_filters import rest_framework as filters
from rest_framework import filters as drf_filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from apps.audit.models import AuditLog
from apps.audit.serializers import AuditLogDetailSerializer, AuditLogListSerializer
from apps.core.permissions import IsSuperAdmin
from apps.core.responses import APIResponse


class AuditLogFilter(filters.FilterSet):
    user = filters.UUIDFilter(field_name='user_id')
    module = filters.CharFilter(field_name='module')
    action = filters.CharFilter(field_name='action')
    ip_address = filters.CharFilter(field_name='ip_address', lookup_expr='icontains')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    response_status = filters.NumberFilter(field_name='response_status')

    class Meta:
        model = AuditLog
        fields = ['user', 'module', 'action', 'ip_address', 'response_status']


class AuditLogViewSet(ReadOnlyModelViewSet):
    """Super-admin read-only access to persisted audit logs."""

    queryset = AuditLog.objects.select_related('user').all()
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    filter_backends = [
        filters.DjangoFilterBackend,
        drf_filters.SearchFilter,
        drf_filters.OrderingFilter,
    ]
    filterset_class = AuditLogFilter
    search_fields = ['object_repr', 'request_path', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'duration_ms', 'response_status', 'module', 'action']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AuditLogDetailSerializer
        return AuditLogListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, AuditLogListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return APIResponse.success(AuditLogDetailSerializer(instance).data)


class AuditUserActivityView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, user_id):
        queryset = (
            AuditLog.objects.filter(user_id=user_id)
            .select_related('user')
            .order_by('-created_at')[:100]
        )
        return APIResponse.success(AuditLogListSerializer(queryset, many=True).data)


class AuditLogExportView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        import csv
        from django.http import HttpResponse

        queryset = AuditLog.objects.select_related('user').order_by('-created_at')[:5000]
        module = request.query_params.get('module')
        if module:
            queryset = queryset.filter(module=module)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        writer = csv.writer(response)
        writer.writerow(
            ['created_at', 'user', 'module', 'action', 'object_repr', 'ip_address', 'response_status', 'duration_ms'],
        )
        for row in queryset:
            writer.writerow(
                [
                    row.created_at.isoformat(),
                    row.user.email if row.user_id else '',
                    row.module,
                    row.action,
                    row.object_repr,
                    row.ip_address,
                    row.response_status,
                    row.duration_ms,
                ],
            )
        return response


class AuditStatsView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        by_module = (
            AuditLog.objects.values('module')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
        by_action = (
            AuditLog.objects.values('action')
            .annotate(count=Count('id'))
            .order_by('-count')[:20]
        )
        return APIResponse.success(
            {
                'by_module': list(by_module),
                'by_action': list(by_action),
                'total': AuditLog.objects.count(),
            }
        )
