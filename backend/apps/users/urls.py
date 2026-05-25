from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.users.views import ModuleViewSet, ProfilePhotoView, ProfileView, RoleViewSet, UserViewSet

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('roles', RoleViewSet, basename='roles')
router.register('modules', ModuleViewSet, basename='modules')

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/photo/', ProfilePhotoView.as_view(), name='profile-photo'),
    path('', include(router.urls)),
]
