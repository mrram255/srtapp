from django.urls import path

from .views import (
    TeacherDashboardView,
    TeacherDetailView,
    TeacherListView,
    TeacherSubjectAssignmentListView,
)

urlpatterns = [
    path('', TeacherListView.as_view(), name='teacher_list'),
    path('dashboard/', TeacherDashboardView.as_view(), name='teacher_dashboard'),
    path('assignments/', TeacherSubjectAssignmentListView.as_view(), name='teacher_subject_assignment_list'),
    path('<uuid:pk>/', TeacherDetailView.as_view(), name='teacher_detail'),
]
