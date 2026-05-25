from django.urls import path

from .views import (
    AcademicYearListView,
    BranchListView,
    CollegeDetailView,
    CollegeListView,
    DepartmentDetailView,
    DepartmentListView,
)

urlpatterns = [
    path('', CollegeListView.as_view(), name='college_list'),
    path('<uuid:pk>/', CollegeDetailView.as_view(), name='college_detail'),
    path('departments/', DepartmentListView.as_view(), name='department_list'),
    path('departments/<uuid:pk>/', DepartmentDetailView.as_view(), name='department_detail'),
    path('branches/', BranchListView.as_view(), name='branch_list'),
    path('academic-years/', AcademicYearListView.as_view(), name='academic_year_list'),
]
