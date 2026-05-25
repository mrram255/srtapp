from __future__ import annotations

import io
from typing import Any

from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.middleware import get_current_user


class CreatedByMixin:
    """Auto-set created_by / updated_by from request.user."""

    created_by_field = 'created_by'
    updated_by_field = 'updated_by'

    def perform_create(self, serializer):
        user = getattr(self.request, 'user', None)
        extra = {}
        if user and user.is_authenticated:
            extra[self.created_by_field] = user
            extra[self.updated_by_field] = user
        serializer.save(**extra)

    def perform_update(self, serializer):
        user = getattr(self.request, 'user', None)
        extra = {}
        if user and user.is_authenticated:
            extra[self.updated_by_field] = user
        serializer.save(**extra)


class SoftDeleteMixin:
    """Soft delete records by setting is_active=False."""

    active_field = 'is_active'

    def perform_destroy(self, instance):
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete(user=getattr(self.request, 'user', None))
            return
        setattr(instance, self.active_field, False)
        instance.save(update_fields=[self.active_field])


class SlugMixin:
    """Auto-generate slug from configured source field."""

    slug_field = 'slug'
    slug_source_field = 'name'

    def perform_create(self, serializer):
        data = serializer.validated_data
        slug_value = data.get(self.slug_field)
        source_value = data.get(self.slug_source_field)
        if not slug_value and source_value:
            serializer.save(**{self.slug_field: slugify(source_value)})
        else:
            serializer.save()

    def perform_update(self, serializer):
        data = serializer.validated_data
        slug_value = data.get(self.slug_field)
        source_value = data.get(self.slug_source_field)
        if source_value and (slug_value is None or slug_value == ''):
            serializer.save(**{self.slug_field: slugify(source_value)})
        else:
            serializer.save()


class ExportMixin:
    """Add export actions to ViewSets."""

    @action(detail=False, methods=['get'], url_path='export/excel')
    def export_to_excel(self, request, *args, **kwargs):
        from apps.core.services import ExcelService

        queryset = self.filter_queryset(self.get_queryset())
        rows = []
        for obj in queryset[:5000]:
            rows.append({'id': str(getattr(obj, 'id', '')), 'repr': str(obj)})
        content = ExcelService.generate_workbook('Export', rows)
        return Response(
            content,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='export/pdf')
    def export_to_pdf(self, request, *args, **kwargs):
        from apps.core.services import PDFService

        queryset = self.filter_queryset(self.get_queryset())
        lines = [str(obj) for obj in queryset[:5000]]
        content = PDFService.generate_simple_pdf('Export', lines)
        return Response(content, content_type='application/pdf', status=status.HTTP_200_OK)


class BulkOperationMixin:
    """Bulk create, update, and soft-delete helpers."""

    @action(detail=False, methods=['post'], url_path='bulk-create')
    def bulk_create(self, request, *args, **kwargs):
        payload = request.data if isinstance(request.data, list) else request.data.get('items', [])
        serializer = self.get_serializer(data=payload, many=True)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            instances = serializer.save()
        return Response(
            {'success': True, 'count': len(instances), 'data': self.get_serializer(instances, many=True).data},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=['patch'], url_path='bulk-update')
    def bulk_update(self, request, *args, **kwargs):
        items = request.data.get('items', [])
        updated = 0
        with transaction.atomic():
            for item in items:
                obj_id = item.get('id')
                if not obj_id:
                    continue
                instance = self.get_queryset().filter(pk=obj_id).first()
                if not instance:
                    continue
                serializer = self.get_serializer(instance, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated += 1
        return Response({'success': True, 'updated': updated})

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request, *args, **kwargs):
        ids = request.data.get('ids', [])
        queryset = self.get_queryset().filter(pk__in=ids)
        deleted = 0
        with transaction.atomic():
            for instance in queryset:
                if hasattr(instance, 'soft_delete'):
                    instance.soft_delete(user=getattr(request, 'user', None))
                elif hasattr(instance, 'is_active'):
                    instance.is_active = False
                    instance.save(update_fields=['is_active'])
                else:
                    instance.delete()
                deleted += 1
        return Response({'success': True, 'deleted': deleted})


def apply_created_by(instance, user=None):
    """Utility for model saves outside ViewSets."""
    actor = user or get_current_user()
    if actor and actor.is_authenticated:
        if hasattr(instance, 'created_by') and instance.created_by_id is None:
            instance.created_by = actor
        if hasattr(instance, 'updated_by'):
            instance.updated_by = actor
