from django.urls import path

from .views import (
    AnnouncementDetailView,
    AnnouncementListView,
    AnnouncementPublishView,
    BulkNotificationHistoryView,
    BulkNotificationSendView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    NotificationPreferenceView,
    NotificationTemplateDetailView,
    NotificationTemplateListView,
    NotificationUnreadCountView,
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification_list'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification_unread_count'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification_mark_all_read'),
    path('preferences/', NotificationPreferenceView.as_view(), name='notification_preferences'),
    path('templates/', NotificationTemplateListView.as_view(), name='notification_templates'),
    path('templates/<uuid:pk>/', NotificationTemplateDetailView.as_view(), name='notification_template_detail'),
    path('send-bulk/', BulkNotificationSendView.as_view(), name='notification_send_bulk'),
    path('bulk-history/', BulkNotificationHistoryView.as_view(), name='notification_bulk_history'),
    path('announcements/', AnnouncementListView.as_view(), name='announcement_list'),
    path('announcements/<uuid:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcements/<uuid:pk>/publish/', AnnouncementPublishView.as_view(), name='announcement_publish'),
    path('<uuid:pk>/read/', NotificationMarkReadView.as_view(), name='notification_mark_read'),
]
