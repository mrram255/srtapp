from django.urls import path

from .views import CompanyListView, JobPostingListView, PlacementApplicationListView

urlpatterns = [
    path('', JobPostingListView.as_view(), name='placement_jobs_root'),
    path('companies/', CompanyListView.as_view(), name='company_list'),
    path('jobs/', JobPostingListView.as_view(), name='job_posting_list'),
    path('applications/', PlacementApplicationListView.as_view(), name='placement_application_list'),
]
