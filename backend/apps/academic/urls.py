from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.academic.views import (
    AcademicCalendarView,
    AcademicEventViewSet,
    AcademicYearViewSet,
    BatchViewSet,
    DepartmentViewSet,
    HolidayViewSet,
    ProgramViewSet,
    RegulationViewSet,
    SectionViewSet,
    SemesterViewSet,
    SubjectViewSet,
)

router = DefaultRouter()
router.register('academic-years', AcademicYearViewSet, basename='academic-years')
router.register('departments', DepartmentViewSet, basename='departments')
router.register('programs', ProgramViewSet, basename='programs')
router.register('regulations', RegulationViewSet, basename='regulations')
router.register('batches', BatchViewSet, basename='batches')
router.register('sections', SectionViewSet, basename='sections')
router.register('semesters', SemesterViewSet, basename='semesters')
router.register('subjects', SubjectViewSet, basename='subjects')
router.register('holidays', HolidayViewSet, basename='holidays')
router.register('academic-events', AcademicEventViewSet, basename='academic-events')

urlpatterns = [
    path('academic-calendar/', AcademicCalendarView.as_view(), name='academic-calendar'),
    path('', include(router.urls)),
]
