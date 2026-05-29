from django.contrib import admin

from .models import (
    Announcement,
    BulkNotification,
    Notification,
    NotificationPreference,
    NotificationTemplate,
    UserNotification,
)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'event_type', 'college', 'is_active']
    list_filter = ['event_type', 'is_active']
    search_fields = ['name']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_enabled', 'sms_enabled', 'push_enabled']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'notification_type',
        'category',
        'priority',
        'recipients',
        'sent_at',
        'is_active',
        'college',
    ]
    list_filter = ['notification_type', 'category', 'priority', 'recipients', 'is_active']
    search_fields = ['title', 'message']


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification', 'is_read', 'is_delivered', 'college']
    list_filter = ['is_read', 'is_delivered']


@admin.register(BulkNotification)
class BulkNotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_type', 'status', 'sent_count', 'college', 'sent_at']
    list_filter = ['status', 'target_type']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement_type', 'target_audience', 'is_pinned', 'published_at', 'college']
    list_filter = ['announcement_type', 'target_audience', 'is_pinned']
