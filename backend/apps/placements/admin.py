from django.contrib import admin

from .models import Company, JobPosting, PlacementApplication


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'industry', 'is_active', 'college']
    search_fields = ['name']


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'status', 'application_deadline']
    list_filter = ['status', 'job_type']


@admin.register(PlacementApplication)
class PlacementApplicationAdmin(admin.ModelAdmin):
    list_display = ['student', 'job', 'status', 'applied_at']
    list_filter = ['status']
