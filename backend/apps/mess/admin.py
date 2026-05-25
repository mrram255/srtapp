from django.contrib import admin

from .models import MessFeedback, MessMenu


@admin.register(MessMenu)
class MessMenuAdmin(admin.ModelAdmin):
    list_display = ['day', 'meal_type', 'is_active', 'college']
    list_filter = ['day', 'meal_type']


@admin.register(MessFeedback)
class MessFeedbackAdmin(admin.ModelAdmin):
    list_display = ['student', 'menu', 'rating', 'date']
    list_filter = ['rating']
