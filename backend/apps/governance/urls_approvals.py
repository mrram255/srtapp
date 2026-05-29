from django.urls import path

from .views import ApprovalDetailView, ApprovalListView

urlpatterns = [
    path('', ApprovalListView.as_view(), name='approvals_root'),
    path('<uuid:pk>/approve/', ApprovalDetailView.as_view(), kwargs={'action': 'approve'}, name='approvals_approve'),
    path('<uuid:pk>/reject/', ApprovalDetailView.as_view(), kwargs={'action': 'reject'}, name='approvals_reject'),
]
