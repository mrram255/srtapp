from django.utils import timezone
from rest_framework import serializers

from apps.accounts.models import User

from .models import (
    Announcement,
    BulkNotification,
    Notification,
    NotificationPreference,
    NotificationTemplate,
    UserNotification,
)


class NotificationBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'message',
            'notification_type',
            'category',
            'priority',
            'action_url',
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
            'channels_sent',
            'metadata',
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
            'category',
            'priority',
            'recipients',
            'specific_user_ids',
            'attachment',
            'image',
            'action_url',
            'scheduled_at',
            'expires_at',
            'send_push',
            'send_email',
            'send_sms',
            'send_whatsapp',
        ]

    def validate(self, attrs):
        recipients = attrs.get('recipients', 'ALL')
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
        )

        if specific_user_ids:
            notification.specific_users.set(
                User.objects.filter(id__in=specific_user_ids, college_id=college.id),
            )
        return notification


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            'email_enabled',
            'sms_enabled',
            'whatsapp_enabled',
            'push_enabled',
            'dnd_start_time',
            'dnd_end_time',
            'category_preferences',
            'updated_at',
        ]
        read_only_fields = ['updated_at']


class NotificationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationTemplate
        fields = [
            'id',
            'college',
            'name',
            'event_type',
            'email_subject',
            'email_body',
            'sms_body',
            'whatsapp_body',
            'push_title',
            'push_body',
            'variables',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BulkNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkNotification
        fields = [
            'id',
            'title',
            'message',
            'category',
            'priority',
            'target_type',
            'target_filters',
            'channels',
            'status',
            'total_recipients',
            'sent_count',
            'failed_count',
            'scheduled_at',
            'sent_at',
            'notification',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'status',
            'total_recipients',
            'sent_count',
            'failed_count',
            'sent_at',
            'notification',
            'created_at',
        ]


class BulkNotificationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = BulkNotification
        fields = [
            'title',
            'message',
            'category',
            'priority',
            'target_type',
            'target_filters',
            'channels',
            'scheduled_at',
        ]

    def validate_channels(self, value):
        if not value:
            return {'in_app': True, 'push': True}
        return value


class AnnouncementSerializer(serializers.ModelSerializer):
    target_department_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list,
    )
    target_program_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        default=list,
    )

    class Meta:
        model = Announcement
        fields = [
            'id',
            'title',
            'content',
            'attachment',
            'announcement_type',
            'target_audience',
            'target_department_ids',
            'target_program_ids',
            'published_at',
            'expires_at',
            'is_pinned',
            'is_active',
            'notification',
            'created_at',
        ]
        read_only_fields = ['id', 'published_at', 'notification', 'created_at']

    def create(self, validated_data):
        dept_ids = validated_data.pop('target_department_ids', [])
        program_ids = validated_data.pop('target_program_ids', [])
        college = self.context['college']
        published_by = self.context.get('published_by')
        announcement = Announcement.objects.create(
            **validated_data,
            college=college,
            published_by=published_by,
        )
        if dept_ids:
            announcement.target_departments.set(dept_ids)
        if program_ids:
            announcement.target_programs.set(program_ids)
        return announcement

    def update(self, instance, validated_data):
        dept_ids = validated_data.pop('target_department_ids', None)
        program_ids = validated_data.pop('target_program_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if dept_ids is not None:
            instance.target_departments.set(dept_ids)
        if program_ids is not None:
            instance.target_programs.set(program_ids)
        return instance
