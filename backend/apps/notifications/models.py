from django.db import models

from apps.core.models import CollegeScopedModel


class Notification(CollegeScopedModel):
    PRIORITY_CHOICES = [
        ('LOW', 'Low'),
        ('NORMAL', 'Normal'),
        ('HIGH', 'High'),
        ('URGENT', 'Urgent'),
    ]

    TYPE_CHOICES = [
        ('ANNOUNCEMENT', 'Announcement'),
        ('EVENT', 'Event'),
        ('EXAM', 'Exam'),
        ('FEE', 'Fee'),
        ('ATTENDANCE', 'Attendance'),
        ('ASSIGNMENT', 'Assignment'),
        ('RESULT', 'Result'),
        ('EMERGENCY', 'Emergency'),
        ('GENERAL', 'General'),
    ]

    RECIPIENT_CHOICES = [
        ('ALL', 'All'),
        ('STUDENTS', 'Students'),
        ('TEACHERS', 'Teachers'),
        ('PARENTS', 'Parents'),
        ('ADMINS', 'Admins'),
        ('HOD', 'HODs'),
        ('SPECIFIC', 'Specific Users'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='GENERAL')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    recipients = models.CharField(max_length=15, choices=RECIPIENT_CHOICES, default='ALL')
    specific_users = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='specific_notifications',
    )

    attachment = models.CharField(max_length=500, blank=True)
    image = models.CharField(max_length=500, blank=True)

    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    sent_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
    )
    total_recipients = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)

    send_push = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.notification_type})'


class UserNotification(CollegeScopedModel):
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='user_notifications',
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        related_name='user_notifications',
    )
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_notifications'
        unique_together = [['user', 'notification']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.notification.title}'
