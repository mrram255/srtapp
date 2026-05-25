from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User

from .models import Notification, UserNotification


class NotificationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'priority',
            'attachment',
            'image',
            'sent_at',
            'expires_at',
            'is_active',
            'created_at',
        ]
        read_only_fields = fields


class UserNotificationSerializer(serializers.ModelSerializer):
    notification = NotificationBriefSerializer(read_only=True)

    class Meta:
        model = UserNotification
        fields = [
            'id',
            'college',
            'notification',
            'is_read',
            'read_at',
            'is_delivered',
            'delivered_at',
            'created_at',
        ]
        read_only_fields = fields


class NotificationWriteSerializer(serializers.ModelSerializer):
    specific_user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list,
    )

    class Meta:
        model = Notification
        fields = [
            'title',
            'message',
            'notification_type',
            'priority',
            'recipients',
            'specific_user_ids',
            'attachment',
            'image',
            'scheduled_at',
            'expires_at',
            'send_push',
            'send_email',
            'send_sms',
        ]

    def validate(self, attrs):
        recipients = attrs.get('recipients', Notification.RECIPIENT_CHOICES[0][0])
        raw_ids = attrs.get('specific_user_ids') or []
        if recipients == 'SPECIFIC' and not raw_ids:
            raise serializers.ValidationError({'specific_user_ids': 'Required when recipients is SPECIFIC.'})
        college = self.context.get('college')
        if recipients == 'SPECIFIC' and college:
            users = User.objects.filter(id__in=raw_ids, college_id=college.id, is_deleted=False)
            if users.count() != len(set(raw_ids)):
                raise serializers.ValidationError({'specific_user_ids': 'Invalid user ids for this college.'})
        return attrs

    def create(self, validated_data):
        specific_user_ids = validated_data.pop('specific_user_ids', [])
        college = self.context['college']
        sent_by = self.context.get('sent_by')

        notification = Notification.objects.create(
            **validated_data,
            college=college,
            sent_by=sent_by,
            sent_at=timezone.now(),
        )

        if specific_user_ids:
            notification.specific_users.set(
                User.objects.filter(id__in=specific_user_ids, college_id=college.id),
            )

        recipient_users = self._expand_recipients(notification)
        notification.total_recipients = len(recipient_users)
        notification.delivered_count = len(recipient_users)
        notification.save(update_fields=['total_recipients', 'delivered_count'])

        college_id = college.id
        UserNotification.objects.bulk_create(
            [
                UserNotification(
                    user=u,
                    notification=notification,
                    college_id=college_id,
                    is_delivered=True,
                    delivered_at=timezone.now(),
                )
                for u in recipient_users
            ],
            ignore_conflicts=True,
        )

        return notification

    def _expand_recipients(self, notification: Notification):
        college_id = notification.college_id
        base = User.objects.filter(college_id=college_id, is_deleted=False, is_active=True)

        key = notification.recipients
        if key == 'SPECIFIC':
            return list(notification.specific_users.all())
        if key == 'ALL':
            return list(base)
        if key == 'STUDENTS':
            return list(base.filter(role='STUDENT'))
        if key == 'TEACHERS':
            return list(base.filter(role='TEACHER'))
        if key == 'PARENTS':
            return list(base.filter(role='PARENT'))
        if key == 'ADMINS':
            return list(base.filter(role='ADMIN'))
        if key == 'HOD':
            return list(base.filter(role='HOD'))
        return list(base)
