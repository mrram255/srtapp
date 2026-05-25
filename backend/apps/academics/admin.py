from django.contrib import admin

from .models import Course, Subject, Timetable


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'college', 'credits', 'is_active']
    list_filter = ['college', 'is_active']
    search_fields = ['name', 'code']
    raw_id_fields = ['college']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course', 'department', 'semester', 'credits', 'is_active']
    list_filter = ['semester', 'is_active', 'college']
    search_fields = ['name', 'code']
    raw_id_fields = ['college', 'course', 'department']


@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ['subject', 'teacher', 'day', 'start_time', 'end_time', 'room_number', 'semester', 'section']
    list_filter = ['day', 'semester', 'section', 'college']
    raw_id_fields = ['college', 'subject', 'teacher', 'department', 'academic_year']
