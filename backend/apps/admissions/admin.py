from django.contrib import admin

from .models import AdmissionApplication


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = ['application_number', 'first_name', 'last_name', 'status', 'department', 'college']
    list_filter = ['status', 'department']
    search_fields = ['application_number', 'first_name', 'last_name', 'email']
