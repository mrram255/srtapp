from django.urls import path
from .views import (
    StudentDashboardView,
    StudentDetailView,
    StudentDocumentListView,
    StudentListView,
    StudentProfileView,
    StudentIDCardView,
    StudentIDVerifyView,
    UniversalIDCardView,
    StudentPhotoUploadView,
    StudentSignatureUploadView,
)

urlpatterns = [
    path('', StudentListView.as_view(), name='student_list'),
    path('dashboard/', StudentDashboardView.as_view(), name='student_dashboard'),
    path('documents/', StudentDocumentListView.as_view(), name='student_document_list'),
    path('me/', StudentProfileView.as_view(), name='student_me'),
    path('photo/upload/', StudentPhotoUploadView.as_view(), name='student_photo_upload'),
    path('signature/upload/', StudentSignatureUploadView.as_view(), name='student_signature_upload'),
    path('id-card/', StudentIDCardView.as_view(), name='student_id_card'),
    path('id-card/me/', UniversalIDCardView.as_view(), name='my_id_card'),
    path('verify/<uuid:student_id>/', StudentIDVerifyView.as_view(), name='student_verify'),
    path('<uuid:pk>/', StudentDetailView.as_view(), name='student_detail'),
]
