from django.contrib import admin

from apps.institutions.models import Institution, InstitutionSettings


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution_type', 'city', 'is_active')
    search_fields = ('name', 'code')


@admin.register(InstitutionSettings)
class InstitutionSettingsAdmin(admin.ModelAdmin):
    list_display = ('institution', 'grading_system', 'timezone')
