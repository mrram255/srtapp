from django.urls import path
from .views import StudentPerformanceView, ClassAnalyticsView, DashboardStatsView

urlpatterns = [
    path('student/', StudentPerformanceView.as_view(), name='student_performance'),
    path('class/', ClassAnalyticsView.as_view(), name='class_analytics'),
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard_stats'),
]
