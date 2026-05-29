from django.contrib import admin

from .models import ApprovalRequest, Meeting, StrategicPlanItem


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ['title', 'request_type', 'status', 'college', 'requested_by']
    list_filter = ['status', 'request_type']


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'scheduled_at', 'status', 'college']
    list_filter = ['status']


@admin.register(StrategicPlanItem)
class StrategicPlanItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'target_year', 'status', 'progress_percent', 'college']
