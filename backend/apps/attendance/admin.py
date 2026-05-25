from django.contrib import admin

from .models import Attendance, AttendanceSummary


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'date', 'status', 'teacher']
    list_filter = ['status', 'date']
    date_hierarchy = 'date'
    raw_id_fields = ['college', 'student', 'subject', 'teacher']


@admin.register(AttendanceSummary)
class AttendanceSummaryAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'percentage', 'total_classes']
    list_filter = ['academic_year']
    raw_id_fields = ['college', 'student', 'subject', 'academic_year']
