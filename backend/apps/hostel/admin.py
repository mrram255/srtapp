from django.contrib import admin

from .models import Hostel, HostelAllocation, Room


@admin.register(Hostel)
class HostelAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'capacity', 'occupied_beds', 'is_active', 'college']
    list_filter = ['type', 'is_active']


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'hostel', 'floor', 'capacity', 'occupied', 'is_active']
    list_filter = ['floor', 'is_active']


@admin.register(HostelAllocation)
class HostelAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'room', 'allocation_date', 'status']
    list_filter = ['status']
