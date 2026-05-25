from __future__ import annotations

from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.core.permissions import IsSuperAdmin
from apps.core.responses import APIResponse
from apps.institutions.models import Institution, InstitutionSettings
from apps.institutions.serializers import (
    InstitutionDetailSerializer,
    InstitutionListSerializer,
    InstitutionSettingsSerializer,
    InstitutionWriteSerializer,
)


class InstitutionViewSet(viewsets.ModelViewSet):
    queryset = Institution.objects.select_related('college', 'settings').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code', 'short_name', 'city']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdmin()]

    def get_serializer_class(self):
        if self.action == 'list':
            return InstitutionListSerializer
        if self.action in {'create', 'update', 'partial_update'}:
            return InstitutionWriteSerializer
        return InstitutionDetailSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return APIResponse.paginated(queryset, InstitutionListSerializer, request)

    def retrieve(self, request, *args, **kwargs):
        institution = self.get_object()
        return APIResponse.success(InstitutionDetailSerializer(institution).data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        institution = serializer.save(created_by=request.user, updated_by=request.user)
        InstitutionSettings.objects.get_or_create(institution=institution)
        return APIResponse.success(
            InstitutionDetailSerializer(institution).data,
            message='Institution created.',
            status=201,
        )

    def update(self, request, *args, **kwargs):
        institution = self.get_object()
        serializer = self.get_serializer(institution, data=request.data, partial=kwargs.get('partial', False))
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        institution = serializer.save(updated_by=request.user)
        return APIResponse.success(InstitutionDetailSerializer(institution).data, message='Institution updated.')

    def destroy(self, request, *args, **kwargs):
        institution = self.get_object()
        institution.is_active = False
        institution.save(update_fields=['is_active', 'updated_at'])
        return APIResponse.success(message='Institution deactivated.')

    @action(detail=True, methods=['get', 'patch'], url_path='settings')
    def institution_settings(self, request, pk=None):
        institution = self.get_object()
        settings_obj, _ = InstitutionSettings.objects.get_or_create(institution=institution)
        if request.method == 'GET':
            return APIResponse.success(InstitutionSettingsSerializer(settings_obj).data)
        if not IsSuperAdmin().has_permission(request, self):
            return APIResponse.error(message='Super admin access required.', status=403)
        serializer = InstitutionSettingsSerializer(settings_obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        serializer.save(updated_by=request.user)
        return APIResponse.success(serializer.data, message='Settings updated.')


class InstitutionSettingsListView(APIView):
    """GET/PATCH /api/v1/institutions/settings/ — first institution settings."""

    def get_permissions(self):
        if self.request.method in {'GET', 'HEAD'}:
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsSuperAdmin()]

    def get(self, request):
        settings_obj = InstitutionSettings.objects.select_related('institution').first()
        if not settings_obj:
            return APIResponse.error(message='No institution settings configured.', status=404)
        return APIResponse.success(InstitutionSettingsSerializer(settings_obj).data)

    def patch(self, request):
        settings_obj = InstitutionSettings.objects.select_related('institution').first()
        if not settings_obj:
            return APIResponse.error(message='No institution settings configured.', status=404)
        serializer = InstitutionSettingsSerializer(settings_obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Validation Error', errors=serializer.errors, status=400)
        serializer.save(updated_by=request.user)
        return APIResponse.success(serializer.data, message='Settings updated.')
