from django.utils import timezone

from apps.core.responses import APIResponse
from apps.core.views import BaseAPIView

from .models import UserNotification
from .serializers import NotificationWriteSerializer, UserNotificationSerializer


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

        return APIResponse.paginated(queryset, UserNotificationSerializer, request)

    def post(self, request):
        if request.user.role not in ('SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER'):
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
            message='Notification sent.',
            status=201,
        )


class NotificationMarkReadView(BaseAPIView):
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
    ]

    def post(self, request, pk):
        user_notification = UserNotification.objects.filter(
            notification_id=pk,
            user=request.user,
            is_deleted=False,
        ).first()
        if not user_notification:
            return APIResponse.error(message='Notification not found.', status=404)

        user_notification.is_read = True
        user_notification.read_at = timezone.now()
        user_notification.save(update_fields=['is_read', 'read_at'])

        return APIResponse.success(message='Marked as read.')


class NotificationUnreadCountView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def get(self, request):
        count = UserNotification.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False,
        ).count()
        return APIResponse.success(data={'unread_count': count})


class NotificationMarkAllReadView(BaseAPIView):
    allowed_roles = [
        'SUPER_ADMIN', 'ADMIN', 'HOD', 'TEACHER',
        'STUDENT', 'PARENT', 'ACCOUNTANT', 'LIBRARIAN', 'SECURITY',
    ]

    def post(self, request):
        updated = UserNotification.objects.filter(
            user=request.user,
            is_read=False,
            is_deleted=False,
        ).update(is_read=True, read_at=timezone.now())

        return APIResponse.success(
            data={'marked_read': updated},
            message=f'{updated} notifications marked as read.',
        )
