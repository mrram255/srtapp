from django.db import models

from apps.core.models import CollegeScopedModel


class ApprovalRequest(CollegeScopedModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    TYPE_CHOICES = [
        ('leave', 'Leave'),
        ('purchase', 'Purchase Order'),
        ('event', 'Event'),
        ('admission', 'Admission'),
        ('certificate', 'Certificate'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    request_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='pending', db_index=True)
    requested_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_requests',
    )
    reviewed_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvals_reviewed',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'approval_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.status})'


class Meeting(CollegeScopedModel):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=255)
    agenda = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='scheduled', db_index=True)
    organizer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='meetings_organized',
    )
    attendees = models.ManyToManyField('accounts.User', blank=True, related_name='meetings_attending')
    minutes = models.TextField(blank=True)

    class Meta:
        db_table = 'governance_meetings'
        ordering = ['scheduled_at']

    def __str__(self):
        return self.title


class StrategicPlanItem(CollegeScopedModel):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_year = models.PositiveIntegerField()
    quarter = models.CharField(max_length=2, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default='planned')
    progress_percent = models.PositiveSmallIntegerField(default=0)
    owner = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='strategic_plan_items',
    )

    class Meta:
        db_table = 'strategic_plan_items'
        ordering = ['target_year', 'title']

    def __str__(self):
        return self.title
