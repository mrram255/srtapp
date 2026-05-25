from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.authentication.views import AuthViewSet, SessionViewSet

router = DefaultRouter()
router.register('', AuthViewSet, basename='auth')
router.register('sessions', SessionViewSet, basename='auth-sessions')

urlpatterns = [
    path('', include(router.urls)),
]
