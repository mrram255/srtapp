from django.urls import path

from .views import AdmissionListView

urlpatterns = [
    path('', AdmissionListView.as_view(), name='admission_list'),
]
