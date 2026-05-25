from django.contrib import admin

from .models import Assignment, AssignmentSubmission


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'teacher', 'due_date', 'status']
    list_filter = ['status', 'semester']
    raw_id_fields = ['college', 'subject', 'teacher', 'department']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'status', 'marks_obtained']
    list_filter = ['status']
    raw_id_fields = ['college', 'assignment', 'student', 'graded_by']
