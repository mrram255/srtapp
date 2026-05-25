from django.contrib import admin

from .models import AcademicYear, Branch, College, Department


@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'city', 'established_year', 'is_active']
    list_filter = ['is_active', 'city', 'state']
    search_fields = ['name', 'code', 'city']
    ordering = ['name']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'college', 'hod', 'is_active']
    list_filter = ['is_active', 'college']
    search_fields = ['name', 'code']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'college', 'duration_years', 'is_active']
    list_filter = ['is_active', 'college', 'department']
    search_fields = ['name', 'code']


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'college', 'start_date', 'end_date', 'is_current', 'is_active']
    list_filter = ['is_current', 'is_active', 'college']
    search_fields = ['year']
