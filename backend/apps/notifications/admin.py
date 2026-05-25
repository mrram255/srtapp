from django.contrib import admin

from .models import Notification, UserNotification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'notification_type',
        'priority',
        'recipients',
        'sent_at',
        'is_active',
        'college',
    ]
    list_filter = ['notification_type', 'priority', 'recipients', 'is_active']
    search_fields = ['title', 'message']


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification', 'is_read', 'is_delivered', 'college']
    list_filter = ['is_read', 'is_delivered']
