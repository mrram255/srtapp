from django.contrib import admin

from .models import Teacher, TeacherSubjectAssignment


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'user', 'department', 'designation', 'joining_date', 'is_active']
    list_filter = ['is_active', 'department', 'designation', 'employment_type']
    search_fields = ['employee_id', 'user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'department', 'college']
    date_hierarchy = 'joining_date'


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'semester', 'section', 'academic_year', 'is_primary']
    list_filter = ['semester', 'section', 'is_primary']
    search_fields = ['teacher__user__first_name', 'subject__name']
    raw_id_fields = ['teacher', 'subject', 'academic_year', 'college']
