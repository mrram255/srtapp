from __future__ import annotations

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.template import Context, Template
from django.utils import timezone

from apps.core.services import NotificationService as ChannelService

from .models import (
    Announcement,
    BulkNotification,
    Notification,
    NotificationPreference,
    NotificationTemplate,
    UserNotification,
)

User = get_user_model()


class NotificationDispatchService:
    @staticmethod
    def get_preferences(user) -> NotificationPreference:
        prefs, _ = NotificationPreference.objects.get_or_create(user=user)
        return prefs

    @staticmethod
    def is_dnd_active(prefs: NotificationPreference) -> bool:
        if not prefs.dnd_start_time or not prefs.dnd_end_time:
            return False
        now = timezone.localtime().time()
        start, end = prefs.dnd_start_time, prefs.dnd_end_time
        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    @staticmethod
    def category_allowed(prefs: NotificationPreference, category: str) -> bool:
        cats = prefs.category_preferences or {}
        if not cats:
            return True
        return cats.get(category, True)

    @staticmethod
    def render_template(template: NotificationTemplate, context: dict[str, Any]) -> dict[str, str]:
        def render_field(text: str) -> str:
            if not text:
                return ''
            return Template(text).render(Context(context))

        return {
            'email_subject': render_field(template.email_subject or template.name),
            'email_body': render_field(template.email_body),
            'sms_body': render_field(template.sms_body)[:160],
            'whatsapp_body': render_field(template.whatsapp_body),
            'push_title': render_field(template.push_title or template.name),
            'push_body': render_field(template.push_body),
        }

    @staticmethod
    def channels_for_notification(notification: Notification) -> list[str]:
        channels = ['in_app']
        if notification.send_email:
            channels.append('email')
        if notification.send_sms:
            channels.append('sms')
        if notification.send_whatsapp:
            channels.append('whatsapp')
        if notification.send_push:
            channels.append('push')
        return channels

    @staticmethod
    def deliver_to_user(
        user,
        *,
        title: str,
        message: str,
        channels: list[str],
        email_subject: str | None = None,
    ) -> dict[str, bool]:
        prefs = NotificationDispatchService.get_preferences(user)
        sent: dict[str, bool] = {}
        external_allowed = not NotificationDispatchService.is_dnd_active(prefs)

        active_channels = ['in_app']
        if external_allowed:
            if 'email' in channels and prefs.email_enabled:
                active_channels.append('email')
            if 'sms' in channels and prefs.sms_enabled:
                active_channels.append('sms')
            if 'whatsapp' in channels and prefs.whatsapp_enabled:
                active_channels.append('whatsapp')
            if 'push' in channels and prefs.push_enabled:
                active_channels.append('push')

        if 'email' in active_channels and user.email:
            sent['email'] = ChannelService.send_email(
                user.email,
                email_subject or title,
                message,
            )
        if 'sms' in active_channels and user.phone:
            sent['sms'] = ChannelService.send_sms(user.phone, message[:160])
        if 'whatsapp' in active_channels and user.phone:
            sent['whatsapp'] = ChannelService.send_whatsapp(user.phone, message)
        if 'push' in active_channels:
            sent['push'] = ChannelService.send_push(str(user.id), title, message)
        sent['in_app'] = True
        return sent

    @staticmethod
    def expand_notification_recipients(notification: Notification) -> list:
        college_id = notification.college_id
        base = User.objects.filter(college_id=college_id, is_deleted=False, is_active=True)
        key = notification.recipients
        if key == 'SPECIFIC':
            return list(notification.specific_users.filter(is_deleted=False, is_active=True))
        if key == 'STUDENTS':
            return list(base.filter(role='STUDENT'))
        if key == 'TEACHERS':
            return list(base.filter(role__in=['TEACHER', 'HOD']))
        if key == 'PARENTS':
            return list(base.filter(role='PARENT'))
        if key == 'ADMINS':
            return list(base.filter(role__in=['ADMIN', 'SUPER_ADMIN', 'REGISTRAR']))
        if key == 'HOD':
            return list(base.filter(role='HOD'))
        return list(base)

    @staticmethod
    @transaction.atomic
    def fan_out_notification(notification: Notification, users: list | None = None) -> int:
        users = users or NotificationDispatchService.expand_notification_recipients(notification)
        channels = NotificationDispatchService.channels_for_notification(notification)
        created = 0
        college_id = notification.college_id

        for user in users:
            prefs = NotificationDispatchService.get_preferences(user)
            if not NotificationDispatchService.category_allowed(prefs, notification.category):
                continue

            channels_sent = NotificationDispatchService.deliver_to_user(
                user,
                title=notification.title,
                message=notification.message,
                channels=channels,
            )
            un, was_created = UserNotification.objects.get_or_create(
                user=user,
                notification=notification,
                defaults={
                    'college_id': college_id,
                    'is_delivered': True,
                    'delivered_at': timezone.now(),
                    'channels_sent': channels_sent,
                    'metadata': {'category': notification.category},
                },
            )
            if not was_created:
                un.is_delivered = True
                un.delivered_at = timezone.now()
                un.channels_sent = channels_sent
                un.save(update_fields=['is_delivered', 'delivered_at', 'channels_sent'])
            created += 1

        notification.total_recipients = len(users)
        notification.delivered_count = created
        notification.sent_at = timezone.now()
        notification.save(update_fields=['total_recipients', 'delivered_count', 'sent_at'])
        return created

    @staticmethod
    def resolve_bulk_targets(bulk: BulkNotification) -> list:
        college_id = bulk.college_id
        base = User.objects.filter(college_id=college_id, is_deleted=False, is_active=True)
        filters = bulk.target_filters or {}
        target = bulk.target_type

        if target == 'individual':
            return list(base.filter(id__in=filters.get('user_ids', [])))
        if target == 'role':
            roles = filters.get('roles') or [filters.get('role')]
            roles = [r for r in roles if r]
            return list(base.filter(role__in=roles))
        if target == 'department':
            from apps.students.models import Student

            dept_ids = filters.get('department_ids') or ([filters.get('department_id')] if filters.get('department_id') else [])
            dept_ids = [d for d in dept_ids if d]
            student_user_ids = Student.objects.filter(
                college_id=college_id,
                department_id__in=dept_ids,
                is_deleted=False,
            ).values_list('user_id', flat=True)
            return list(
                base.filter(
                    Q(id__in=list(student_user_ids)) | Q(department_id__in=dept_ids),
                ).distinct(),
            )
        if target == 'program':
            from apps.students.models import Student

            program_ids = filters.get('program_ids') or []
            dept_ids = []
            if program_ids:
                from apps.academic.models import Program

                dept_ids = list(
                    Program.objects.filter(id__in=program_ids).values_list('department_id', flat=True)
                )
            student_users = Student.objects.filter(
                college_id=college_id,
                department_id__in=dept_ids,
                is_deleted=False,
            ).values_list('user_id', flat=True)
            return list(base.filter(id__in=list(student_users)))
        if target == 'batch':
            from apps.students.models import Student

            batch_year = filters.get('batch_year')
            qs = Student.objects.filter(college_id=college_id, is_deleted=False)
            if batch_year:
                qs = qs.filter(batch_year=batch_year)
            return list(base.filter(id__in=qs.values_list('user_id', flat=True)))
        if target == 'section':
            from apps.students.models import Student

            section = filters.get('section')
            qs = Student.objects.filter(college_id=college_id, is_deleted=False)
            if section:
                qs = qs.filter(section__iexact=section)
            return list(base.filter(id__in=qs.values_list('user_id', flat=True)))
        return list(base)

    @staticmethod
    @transaction.atomic
    def process_bulk(bulk: BulkNotification) -> BulkNotification:
        bulk.status = 'sending'
        bulk.save(update_fields=['status'])

        users = NotificationDispatchService.resolve_bulk_targets(bulk)
        channel_map = bulk.channels or {}
        notification = Notification.objects.create(
            college=bulk.college,
            title=bulk.title,
            message=bulk.message,
            category=bulk.category,
            priority=bulk.priority,
            notification_type='GENERAL',
            recipients='SPECIFIC',
            sent_by=bulk.sent_by,
            send_email=channel_map.get('email', False),
            send_sms=channel_map.get('sms', False),
            send_whatsapp=channel_map.get('whatsapp', False),
            send_push=channel_map.get('push', True),
        )
        notification.specific_users.set(users)

        delivered = 0
        failed = 0
        channels = []
        if channel_map.get('in_app', True):
            channels.append('in_app')
        if channel_map.get('email'):
            channels.append('email')
        if channel_map.get('sms'):
            channels.append('sms')
        if channel_map.get('whatsapp'):
            channels.append('whatsapp')
        if channel_map.get('push', True):
            channels.append('push')

        for user in users:
            try:
                prefs = NotificationDispatchService.get_preferences(user)
                if not NotificationDispatchService.category_allowed(prefs, bulk.category):
                    continue
                channels_sent = NotificationDispatchService.deliver_to_user(
                    user,
                    title=bulk.title,
                    message=bulk.message,
                    channels=channels,
                )
                UserNotification.objects.create(
                    user=user,
                    notification=notification,
                    college=bulk.college,
                    is_delivered=True,
                    delivered_at=timezone.now(),
                    channels_sent=channels_sent,
                )
                delivered += 1
            except Exception:
                failed += 1

        bulk.notification = notification
        bulk.total_recipients = len(users)
        bulk.sent_count = delivered
        bulk.failed_count = failed
        bulk.status = 'completed' if failed == 0 else 'completed'
        bulk.sent_at = timezone.now()
        bulk.save(
            update_fields=[
                'notification',
                'total_recipients',
                'sent_count',
                'failed_count',
                'status',
                'sent_at',
            ]
        )
        notification.total_recipients = len(users)
        notification.delivered_count = delivered
        notification.sent_at = timezone.now()
        notification.save(update_fields=['total_recipients', 'delivered_count', 'sent_at'])
        return bulk

    @staticmethod
    @transaction.atomic
    def publish_announcement(announcement: Announcement) -> Announcement:
        users: list = []
        base = User.objects.filter(college_id=announcement.college_id, is_deleted=False, is_active=True)
        if announcement.target_audience == 'students':
            users = list(base.filter(role='STUDENT'))
        elif announcement.target_audience == 'staff':
            users = list(base.exclude(role='STUDENT'))
        elif announcement.target_audience == 'specific_dept':
            from apps.students.models import Student

            dept_ids = list(announcement.target_departments.values_list('id', flat=True))
            student_ids = Student.objects.filter(
                department_id__in=dept_ids,
                college_id=announcement.college_id,
                is_deleted=False,
            ).values_list('user_id', flat=True)
            users = list(
                base.filter(
                    Q(id__in=list(student_ids)) | Q(department_id__in=dept_ids),
                ).distinct(),
            )
        else:
            users = list(base)

        notification = Notification.objects.create(
            college=announcement.college,
            title=announcement.title,
            message=announcement.content,
            category='general',
            notification_type='ANNOUNCEMENT',
            recipients='SPECIFIC',
            sent_by=announcement.published_by,
            send_push=True,
        )
        notification.specific_users.set(users)
        NotificationDispatchService.fan_out_notification(notification, users)

        announcement.notification = notification
        announcement.published_at = timezone.now()
        announcement.save(update_fields=['notification', 'published_at'])
        return announcement

    @staticmethod
    def mark_read(user, notification_id) -> bool:
        updated = UserNotification.objects.filter(
            user=user,
            notification_id=notification_id,
            is_deleted=False,
        ).update(is_read=True, read_at=timezone.now())
        return updated > 0

    @staticmethod
    def mark_all_read(user) -> int:
        return UserNotification.objects.filter(
            user=user,
            is_read=False,
            is_deleted=False,
        ).update(is_read=True, read_at=timezone.now())

    @staticmethod
    def unread_count(user) -> int:
        return UserNotification.objects.filter(
            user=user,
            is_read=False,
            is_deleted=False,
        ).count()

    @staticmethod
    def send_from_template(
        *,
        user,
        template: NotificationTemplate,
        context: dict[str, Any],
        college,
        channels: list[str] | None = None,
    ) -> Notification:
        rendered = NotificationDispatchService.render_template(template, context)
        notification = Notification.objects.create(
            college=college,
            title=rendered['push_title'],
            message=rendered['push_body'] or rendered['email_body'],
            template=template,
            category='general',
            recipients='SPECIFIC',
            send_email='email' in (channels or []),
            send_sms='sms' in (channels or []),
            send_whatsapp='whatsapp' in (channels or []),
            send_push='push' in (channels or ['push']),
        )
        notification.specific_users.set([user])
        NotificationDispatchService.fan_out_notification(notification, [user])
        return notification
