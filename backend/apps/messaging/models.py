from django.db import models

from apps.core.models import CollegeScopedModel


class MessageThread(CollegeScopedModel):
    THREAD_TYPES = [
        ('DIRECT', 'Direct Message'),
        ('GROUP', 'Group Chat'),
        ('ANNOUNCEMENT', 'Announcement'),
    ]

    title = models.CharField(max_length=255, blank=True)
    thread_type = models.CharField(max_length=15, choices=THREAD_TYPES, default='DIRECT')
    participants = models.ManyToManyField('accounts.User', related_name='message_threads')
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='created_threads',
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'message_threads'
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.title or "Untitled"} ({self.thread_type})'


class Message(CollegeScopedModel):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    attachment = models.CharField(max_length=500, blank=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'messages'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender.email}: {self.content[:50]}'
