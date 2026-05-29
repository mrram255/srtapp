from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.audit.views import AuditLogExportView, AuditLogViewSet, AuditStatsView, AuditUserActivityView

router = DefaultRouter()
router.register('logs', AuditLogViewSet, basename='audit-logs')

urlpatterns = [
    path('', include(router.urls)),
    path('export/', AuditLogExportView.as_view(), name='audit-export'),
    path('user/<uuid:user_id>/', AuditUserActivityView.as_view(), name='audit-user-activity'),
    path('stats/', AuditStatsView.as_view(), name='audit-stats'),
]
