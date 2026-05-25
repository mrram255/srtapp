from django.contrib import admin
from .models import Designation, Staff, StaffServiceBook


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'college']
    list_filter = ['category', 'college']
    search_fields = ['name']


class StaffServiceBookInline(admin.TabularInline):
    model = StaffServiceBook
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = [
        'employee_id', 'get_full_name', 'department', 'staff_type',
        'designation', 'status', 'date_of_joining'
    ]
    list_filter = ['staff_type', 'status', 'department', 'phd_status', 'net_set_qualified']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    inlines = [StaffServiceBookInline]

    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Name'


@admin.register(StaffServiceBook)
class StaffServiceBookAdmin(admin.ModelAdmin):
    list_display = ['staff', 'entry_type', 'effective_date', 'order_number']
    list_filter = ['entry_type']
    search_fields = ['staff__employee_id', 'order_number']
