from django.contrib import admin

from .models import Message, MessageThread


@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ['title', 'thread_type', 'created_by', 'is_active', 'college']
    list_filter = ['thread_type', 'is_active']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'thread', 'content_preview', 'is_read', 'created_at']
    list_filter = ['is_read']

    @staticmethod
    def content_preview(obj):
        return obj.content[:50]
