from django.urls import path
from .views import (
    AssignmentListView,
    AssignmentDetailView,
    AssignmentSubmissionListView,
    AssignmentGradeView,
    AssignmentAttachmentUploadView,
)

urlpatterns = [
    path('', AssignmentListView.as_view(), name='assignment_list'),
    path('<uuid:pk>/', AssignmentDetailView.as_view(), name='assignment_detail'),
    path('submissions/', AssignmentSubmissionListView.as_view(), name='assignment_submission_list'),
    path('submissions/<uuid:pk>/grade/', AssignmentGradeView.as_view(), name='assignment_grade'),
    path('attachment/upload/', AssignmentAttachmentUploadView.as_view(), name='assignment_attachment_upload'),
]
