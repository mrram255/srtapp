from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import (
    Announcement,
    BulkNotification,
    NotificationTemplate,
    UserNotification,
)
from .serializers import (
    AnnouncementSerializer,
    BulkNotificationSerializer,
    BulkNotificationWriteSerializer,
    NotificationPreferenceSerializer,
    NotificationTemplateSerializer,
    NotificationWriteSerializer,
    UserNotificationSerializer,
)
from .services import NotificationDispatchService


class NotificationListView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN',
        'ADMIN',
        'HOD',
        'TEACHER',
        'STUDENT',
        'PARENT',
        'ACCOUNTANT',
        'LIBRARIAN',
        'SECURITY',
        'REGISTRAR',
    ]

    def get(self, request):
        queryset = UserNotification.objects.filter(user=request.user, is_deleted=False).select_related(
            'notification',
        )
        if getattr(request.user, 'college_id', None):
            queryset = queryset.filter(college_id=request.user.college_id)

        is_read = request.query_params.get('is_read')
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')

        category = request.query_params.get('category')
        if category:
            queryset = queryset.filter(notification__category=category)

        return APIResponse.paginated(queryset, UserNotificationSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'REGISTRAR'):
            return APIResponse.error(message='Access denied.', status=403)

        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.data.get('college')
            if not college_id:
                return APIResponse.error(message='college is required.', status=400)
            from apps.colleges.models import College

            college = College.objects.filter(pk=college_id, is_deleted=False).first()
            if not college:
                return APIResponse.error(message='Invalid college.', status=400)

        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = NotificationWriteSerializer(
            data=request.data,
            context={'request': request, 'college': college, 'sent_by': request.user},
        )
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        notification = serializer.save()

        from .tasks import send_notification_task

        send_notification_task.delay(str(notification.id))
        return APIResponse.success(
            data={'id': str(notification.id)},
            message='Notification queued.',
            status=201,
        )


class NotificationMarkReadView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'ACCOUNTANT', 'LIBRARIAN', 'SECURITY', 'REGISTRAR',
    ]

    def post(self, request, pk):
        if not NotificationDispatchService.mark_read(request.user, pk):
            return APIResponse.error(message='Notification not found.', status=404)
        return APIResponse.success(message='Marked as read.')


class NotificationUnreadCountView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'ACCOUNTANT', 'LIBRARIAN', 'SECURITY', 'REGISTRAR',
    ]

    def get(self, request):
        count = NotificationDispatchService.unread_count(request.user)
        return APIResponse.success(data={'unread_count': count})


class NotificationMarkAllReadView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'ACCOUNTANT', 'LIBRARIAN', 'SECURITY', 'REGISTRAR',
    ]

    def post(self, request):
        updated = NotificationDispatchService.mark_all_read(request.user)
        return APIResponse.success(
            data={'marked_read': updated},
            message=f'{updated} notifications marked as read.',
        )


class NotificationPreferenceView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'ACCOUNTANT', 'LIBRARIAN', 'SECURITY', 'REGISTRAR',
    ]

    def get(self, request):
        prefs = NotificationDispatchService.get_preferences(request.user)
        return APIResponse.success(data=NotificationPreferenceSerializer(prefs).data)

    def patch(self, request):
        prefs = NotificationDispatchService.get_preferences(request.user)
        serializer = NotificationPreferenceSerializer(prefs, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        return APIResponse.success(data=serializer.data, message='Preferences updated.')


class NotificationTemplateListView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR']

    def get(self, request):
        queryset = NotificationTemplate.objects.filter(is_active=True)
        if request.user.role != 'SUPER_ADMIN' and request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        college_id = request.query_params.get('college')
        if college_id and request.user.role == 'SUPER_ADMIN':
            queryset = queryset.filter(college_id=college_id)
        return APIResponse.paginated(queryset, NotificationTemplateSerializer, request)

    def post(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.data.get('college')
            if college_id:
                from apps.colleges.models import College

                college = College.objects.filter(pk=college_id, is_deleted=False).first()
        serializer = NotificationTemplateSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save(college=college)
        return APIResponse.success(data=serializer.data, message='Template created.', status=201)


class NotificationTemplateDetailView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR']

    def get_object(self, request, pk):
        queryset = NotificationTemplate.objects.filter(pk=pk, is_active=True)
        if request.user.role != 'SUPER_ADMIN' and request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        return queryset.first()

    def get(self, request, pk):
        obj = self.get_object(request, pk)
        if not obj:
            return APIResponse.error(message='Template not found.', status=404)
        return APIResponse.success(data=NotificationTemplateSerializer(obj).data)

    def patch(self, request, pk):
        obj = self.get_object(request, pk)
        if not obj:
            return APIResponse.error(message='Template not found.', status=404)
        serializer = NotificationTemplateSerializer(obj, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        return APIResponse.success(data=serializer.data, message='Template updated.')

    def delete(self, request, pk):
        obj = self.get_object(request, pk)
        if not obj:
            return APIResponse.error(message='Template not found.', status=404)
        obj.is_active = False
        obj.save(update_fields=['is_active'])
        return APIResponse.success(message='Template deleted.')


class BulkNotificationSendView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR']

    def post(self, request):
        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.data.get('college')
            if college_id:
                from apps.colleges.models import College

                college = College.objects.filter(pk=college_id, is_deleted=False).first()
        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = BulkNotificationWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)

        bulk = BulkNotification.objects.create(
            **serializer.validated_data,
            college=college,
            sent_by=request.user,
            status='queued',
        )

        from .tasks import send_bulk_notification_task

        send_bulk_notification_task.delay(str(bulk.id))
        return APIResponse.success(
            data=BulkNotificationSerializer(bulk).data,
            message='Bulk notification queued.',
            status=201,
        )


class BulkNotificationHistoryView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR']

    def get(self, request):
        queryset = BulkNotification.objects.filter(is_deleted=False).select_related('sent_by')
        if request.user.role != 'SUPER_ADMIN' and request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        return APIResponse.paginated(queryset, BulkNotificationSerializer, request)


class AnnouncementListView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'REGISTRAR', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def get(self, request):
        queryset = Announcement.objects.filter(is_deleted=False, is_active=True)
        if request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        return APIResponse.paginated(queryset, AnnouncementSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        college = request.user.college
        if request.user.role == 'SUPER_ADMIN':
            college_id = request.data.get('college')
            if college_id:
                from apps.colleges.models import College

                college = College.objects.filter(pk=college_id, is_deleted=False).first()
        if college is None:
            return APIResponse.error(message='College context required.', status=400)

        serializer = AnnouncementSerializer(
            data=request.data,
            context={'college': college, 'published_by': request.user},
        )
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        announcement = serializer.save()
        return APIResponse.success(
            data=AnnouncementSerializer(announcement).data,
            message='Announcement created.',
            status=201,
        )


class AnnouncementDetailView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER', 'STUDENT', 'PARENT',
        'REGISTRAR', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def get(self, request, pk):
        queryset = Announcement.objects.filter(pk=pk, is_deleted=False)
        if request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        announcement = queryset.first()
        if not announcement:
            return APIResponse.error(message='Announcement not found.', status=404)
        return APIResponse.success(data=AnnouncementSerializer(announcement).data)

    def patch(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'HOD'):
            return APIResponse.error(message='Access denied.', status=403)

        queryset = Announcement.objects.filter(pk=pk, is_deleted=False)
        if request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        announcement = queryset.first()
        if not announcement:
            return APIResponse.error(message='Announcement not found.', status=404)

        serializer = AnnouncementSerializer(announcement, data=request.data, partial=True)
        if not serializer.is_valid():
            return APIResponse.error(message='Invalid input.', errors=serializer.errors)
        serializer.save()
        return APIResponse.success(data=serializer.data, message='Announcement updated.')

    def delete(self, request, pk):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'REGISTRAR'):
            return APIResponse.error(message='Access denied.', status=403)

        queryset = Announcement.objects.filter(pk=pk, is_deleted=False)
        if request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        announcement = queryset.first()
        if not announcement:
            return APIResponse.error(message='Announcement not found.', status=404)
        announcement.soft_delete(user=request.user)
        return APIResponse.success(message='Announcement deleted.')


class AnnouncementPublishView(BaseAPIView):
    allowed_roles = ['SUPER_ADMIN', 'ADMIN', 'REGISTRAR', 'HOD']

    def post(self, request, pk):
        queryset = Announcement.objects.filter(pk=pk, is_deleted=False)
        if request.user.college_id:
            queryset = queryset.filter(college_id=request.user.college_id)
        announcement = queryset.first()
        if not announcement:
            return APIResponse.error(message='Announcement not found.', status=404)

        if announcement.published_at:
            return APIResponse.error(message='Announcement already published.', status=400)

        announcement = NotificationDispatchService.publish_announcement(announcement)
        return APIResponse.success(
            data=AnnouncementSerializer(announcement).data,
            message='Announcement published.',
        )
