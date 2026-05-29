from django.urls import path

from .views import (
    AdmissionCycleListView,
    AdmissionDetailView,
    AdmissionEnrollView,
    AdmissionInquiryListView,
    AdmissionKanbanView,
    AdmissionListView,
    MeritListView,
    PublicAdmissionApplyView,
)

urlpatterns = [
    path('', AdmissionListView.as_view(), name='admission_list'),
    path('apply/', PublicAdmissionApplyView.as_view(), name='admission_public_apply'),
    path('cycles/', AdmissionCycleListView.as_view(), name='admission_cycles'),
    path('inquiries/', AdmissionInquiryListView.as_view(), name='admission_inquiries'),
    path('kanban/', AdmissionKanbanView.as_view(), name='admission_kanban'),
    path('merit-lists/', MeritListView.as_view(), name='merit_lists'),
    path('<uuid:pk>/', AdmissionDetailView.as_view(), name='admission_detail'),
    path('<uuid:pk>/enroll/', AdmissionEnrollView.as_view(), name='admission_enroll'),
]
