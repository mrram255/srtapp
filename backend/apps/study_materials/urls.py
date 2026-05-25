from django.urls import path
from .views import StudyMaterialListView, StudyMaterialDetailView, StudyMaterialUploadView

urlpatterns = [
    path('', StudyMaterialListView.as_view(), name='study_material_list'),
    path('upload/', StudyMaterialUploadView.as_view(), name='study_material_upload'),
    path('<uuid:pk>/', StudyMaterialDetailView.as_view(), name='study_material_detail'),
]
