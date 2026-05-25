from django.contrib import admin

from .models import ExamResult, ExamSchedule


@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'exam_type', 'subject', 'exam_date', 'start_time', 'is_active']
    list_filter = ['exam_type', 'is_active']
    date_hierarchy = 'exam_date'
    raw_id_fields = ['college', 'subject', 'department']


@admin.register(ExamResult)
class ExamResultAdmin(admin.ModelAdmin):
    list_display = ['exam', 'student', 'marks_obtained', 'status', 'percentage']
    list_filter = ['status']
    raw_id_fields = ['college', 'exam', 'student', 'evaluated_by']
