from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.institutions.views import InstitutionSettingsListView, InstitutionViewSet

router = DefaultRouter()
router.register('institutions', InstitutionViewSet, basename='institutions')

urlpatterns = [
    path('institutions/settings/', InstitutionSettingsListView.as_view(), name='institution-settings'),
    path('', include(router.urls)),
]
