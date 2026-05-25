from django.contrib import admin

from .models import Event, EventRegistration


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'start_datetime', 'venue', 'is_active']
    list_filter = ['event_type', 'is_active']
    date_hierarchy = 'start_datetime'


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['event', 'user', 'status', 'registered_at']
    list_filter = ['status']
