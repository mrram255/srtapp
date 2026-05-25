from django.contrib import admin

from .models import Student, StudentDocument


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = [
        'enrollment_number',
        'roll_number',
        'user',
        'department',
        'semester',
        'section',
        'is_active',
    ]
    list_filter = ['is_active', 'department', 'semester', 'section', 'batch_year', 'gender']
    search_fields = ['enrollment_number', 'roll_number', 'user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user', 'department', 'branch', 'academic_year']
    date_hierarchy = 'admission_date'


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'is_verified', 'verified_by', 'created_at']
    list_filter = ['document_type', 'is_verified']
    search_fields = ['student__enrollment_number']
