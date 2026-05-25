from django.urls import path

from .views import (
    CourseListView,
    SubjectListView,
    TimetableListView,
    TimetableDetailView,
    TimetableTodayView,
    TimetableWeekView,
)

urlpatterns = [
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('subjects/', SubjectListView.as_view(), name='subject_list'),
    path('timetable/', TimetableListView.as_view(), name='timetable_list'),
    path('timetable/today/', TimetableTodayView.as_view(), name='timetable_today'),
    path('timetable/week/', TimetableWeekView.as_view(), name='timetable_week'),
    path('timetable/<uuid:pk>/', TimetableDetailView.as_view(), name='timetable_detail'),
]
