from django.urls import path

from .views import (
    AttendanceListView,
    AttendanceSummaryView,
    AttendanceMonthlyStatsView,
    AttendanceAlertView,
)

urlpatterns = [
    path('', AttendanceListView.as_view(), name='attendance_list'),
    path('summary/', AttendanceSummaryView.as_view(), name='attendance_summary'),
    path('monthly-stats/', AttendanceMonthlyStatsView.as_view(), name='attendance_monthly_stats'),
    path('alerts/', AttendanceAlertView.as_view(), name='attendance_alerts'),
]
