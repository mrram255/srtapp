from django.urls import path

from .views import (
    ApprovalDetailView,
    ApprovalListView,
    MeetingDetailView,
    MeetingListView,
    StrategicPlanListView,
)

urlpatterns = [
    path('approvals/', ApprovalListView.as_view(), name='approval_list'),
    path('approvals/<uuid:pk>/approve/', ApprovalDetailView.as_view(), kwargs={'action': 'approve'}, name='approval_approve'),
    path('approvals/<uuid:pk>/reject/', ApprovalDetailView.as_view(), kwargs={'action': 'reject'}, name='approval_reject'),
    path('meetings/', MeetingListView.as_view(), name='meeting_list'),
    path('meetings/<uuid:pk>/', MeetingDetailView.as_view(), name='meeting_detail'),
    path('strategic-plan/', StrategicPlanListView.as_view(), name='strategic_plan_list'),
]
