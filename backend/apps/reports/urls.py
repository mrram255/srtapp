from django.urls import path

from .views import GeneratedReportListView, ReportTemplateListView

urlpatterns = [
    path('templates/', ReportTemplateListView.as_view(), name='report_template_list'),
    path('generated/', GeneratedReportListView.as_view(), name='generated_report_list'),
]
