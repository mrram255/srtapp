from django.contrib import admin

from .models import GateLog


@admin.register(GateLog)
class GateLogAdmin(admin.ModelAdmin):
    list_display = ['entry_type', 'person_type', 'timestamp', 'gate_number', 'security_guard']
    list_filter = ['entry_type', 'person_type', 'gate_number']
    date_hierarchy = 'timestamp'
