from django.contrib import admin

from .models import BusRoute, BusStop, TransportAllocation


@admin.register(BusRoute)
class BusRouteAdmin(admin.ModelAdmin):
    list_display = ['route_number', 'name', 'capacity', 'occupied', 'is_active', 'college']
    list_filter = ['is_active']


@admin.register(BusStop)
class BusStopAdmin(admin.ModelAdmin):
    list_display = ['stop_name', 'route', 'stop_order', 'arrival_time']
    list_filter = ['route']


@admin.register(TransportAllocation)
class TransportAllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'route', 'pickup_stop', 'status']
    list_filter = ['status']
