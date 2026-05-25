from rest_framework.routers import DefaultRouter
from .views import DesignationViewSet, StaffViewSet

router = DefaultRouter()
router.register(r'designations', DesignationViewSet, basename='designation')
router.register(r'staff', StaffViewSet, basename='staff')

urlpatterns = router.urls
