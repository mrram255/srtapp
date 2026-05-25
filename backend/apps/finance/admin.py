from django.contrib import admin

from .models import FeePayment, FeeStructure


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'semester', 'total_fee', 'is_active']
    list_filter = ['semester', 'is_active']
    raw_id_fields = ['college', 'department', 'branch', 'academic_year']


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'fee_structure', 'amount_due', 'amount_paid', 'status', 'due_date']
    list_filter = ['status']
    date_hierarchy = 'due_date'
    raw_id_fields = ['college', 'student', 'fee_structure']
