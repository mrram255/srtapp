from django.db import models

from apps.core.models import CollegeScopedModel, TimeStampedModel


class NotificationTemplate(TimeStampedModel):
    EVENT_TYPES = [
        ('fee_due', 'Fee Due'),
        ('attendance_low', 'Low Attendance'),
        ('result_published', 'Result Published'),
        ('certificate_ready', 'Certificate Ready'),
        ('admission_status', 'Admission Status'),
        ('leave_approved', 'Leave Approved'),
        ('exam_schedule', 'Exam Schedule'),
        ('assignment_due', 'Assignment Due'),
        ('complaint_update', 'Complaint Update'),
        ('custom', 'Custom'),
    ]

    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notification_templates',
    )
    name = models.CharField(max_length=200)
    event_type = models.CharField(max_length=32, choices=EVENT_TYPES, default='custom')
    email_subject = models.CharField(max_length=255, blank=True)
    email_body = models.TextField(blank=True)
    sms_body = models.CharField(max_length=160, blank=True)
    whatsapp_body = models.TextField(blank=True)
    push_title = models.CharField(max_length=255, blank=True)
    push_body = models.TextField(blank=True)
    variables = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'notification_templates'
        ordering = ['name']

    def __str__(self):
        return self.name


class NotificationPreference(models.Model):
    user = models.OneToOneField(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
    )
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=True)
    whatsapp_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    dnd_start_time = models.TimeField(null=True, blank=True)
    dnd_end_time = models.TimeField(null=True, blank=True)
    category_preferences = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notification_preferences'

    def __str__(self):
        return f'Preferences for {self.user_id}'


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
        ('INFO', 'Info'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('ALERT', 'Alert'),
    ]

    CATEGORY_CHOICES = [
        ('academic', 'Academic'),
        ('finance', 'Finance'),
        ('exam', 'Exam'),
        ('admission', 'Admission'),
        ('general', 'General'),
        ('attendance', 'Attendance'),
        ('certificate', 'Certificate'),
        ('placement', 'Placement'),
        ('hostel', 'Hostel'),
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
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    recipients = models.CharField(max_length=15, choices=RECIPIENT_CHOICES, default='ALL')
    specific_users = models.ManyToManyField(
        'accounts.User',
        blank=True,
        related_name='specific_notifications',
    )

    attachment = models.CharField(max_length=500, blank=True)
    image = models.CharField(max_length=500, blank=True)
    action_url = models.CharField(max_length=500, blank=True)

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
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='notifications',
    )
    total_recipients = models.PositiveIntegerField(default=0)
    delivered_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)

    send_push = models.BooleanField(default=True)
    send_email = models.BooleanField(default=False)
    send_sms = models.BooleanField(default=False)
    send_whatsapp = models.BooleanField(default=False)

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
    channels_sent = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'user_notifications'
        unique_together = [['user', 'notification']]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.email} - {self.notification.title}'


class BulkNotification(CollegeScopedModel):
    TARGET_TYPES = [
        ('all', 'All'),
        ('role', 'Role'),
        ('department', 'Department'),
        ('program', 'Program'),
        ('batch', 'Batch'),
        ('section', 'Section'),
        ('individual', 'Individual'),
    ]
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('queued', 'Queued'),
        ('sending', 'Sending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=20, default='general')
    priority = models.CharField(max_length=10, default='NORMAL')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPES, default='all')
    target_filters = models.JSONField(default=dict, blank=True)
    channels = models.JSONField(
        default=dict,
        help_text='{"email": true, "sms": false, "whatsapp": false, "push": true, "in_app": true}',
    )
    sent_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulk_notifications_sent',
    )
    total_recipients = models.PositiveIntegerField(default=0)
    sent_count = models.PositiveIntegerField(default=0)
    failed_count = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='draft', db_index=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bulk_campaigns',
    )

    class Meta:
        db_table = 'bulk_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'


class Announcement(CollegeScopedModel):
    ANNOUNCEMENT_TYPES = [
        ('general', 'General'),
        ('urgent', 'Urgent'),
        ('academic', 'Academic'),
        ('exam', 'Exam'),
        ('placement', 'Placement'),
        ('hostel', 'Hostel'),
        ('event', 'Event'),
        ('holiday', 'Holiday'),
    ]
    TARGET_AUDIENCE = [
        ('all', 'All'),
        ('students', 'Students'),
        ('staff', 'Staff'),
        ('specific_dept', 'Specific Department'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    attachment = models.CharField(max_length=500, blank=True)
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, default='general')
    target_audience = models.CharField(max_length=20, choices=TARGET_AUDIENCE, default='all')
    target_departments = models.ManyToManyField(
        'colleges.Department',
        blank=True,
        related_name='announcements',
    )
    target_programs = models.ManyToManyField(
        'academic.Program',
        blank=True,
        related_name='announcements',
    )
    published_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements_published',
    )
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='announcements',
    )

    class Meta:
        db_table = 'announcements'
        ordering = ['-is_pinned', '-published_at']

    def __str__(self):
        return self.title
