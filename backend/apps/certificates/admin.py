from django.contrib import admin

from .models import CertificateIssue, CertificateRequest, CertificateTemplate


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'certificate_type', 'college', 'requires_approval', 'is_active']
    list_filter = ['certificate_type', 'requires_approval', 'is_active']
    search_fields = ['name', 'code']


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'student', 'template', 'status', 'created_at']
    list_filter = ['status', 'template__certificate_type']
    search_fields = ['request_number', 'student__enrollment_number']


@admin.register(CertificateIssue)
class CertificateIssueAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student', 'template', 'status', 'is_revoked', 'issued_at']
    list_filter = ['status', 'is_revoked', 'template__certificate_type']
    search_fields = ['certificate_number', 'verification_code', 'student__enrollment_number']
