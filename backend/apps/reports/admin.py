from django.contrib import admin

from .models import GeneratedReport, ReportTemplate


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_active', 'college']
    list_filter = ['report_type', 'is_active']


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'status', 'generated_by', 'created_at']
    list_filter = ['status']
