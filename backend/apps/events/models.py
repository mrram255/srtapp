from django.db import models

from apps.core.models import CollegeScopedModel


class Event(CollegeScopedModel):
    EVENT_TYPES = [
        ('ACADEMIC', 'Academic'),
        ('CULTURAL', 'Cultural'),
        ('SPORTS', 'Sports'),
        ('SEMINAR', 'Seminar'),
        ('WORKSHOP', 'Workshop'),
        ('FEST', 'Fest/Festival'),
        ('HOLIDAY', 'Holiday'),
        ('EXAM', 'Exam'),
        ('OTHER', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=15, choices=EVENT_TYPES, default='OTHER')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    venue = models.CharField(max_length=255, blank=True)
    organizer = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organized_events',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
    )
    banner_image = models.CharField(max_length=500, blank=True)
    max_participants = models.PositiveIntegerField(null=True, blank=True)
    registration_required = models.BooleanField(default=False)
    registration_deadline = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'events'
        ordering = ['-start_datetime']

    def __str__(self):
        return f'{self.title} ({self.event_type})'


class EventRegistration(CollegeScopedModel):
    STATUS_CHOICES = [
        ('REGISTERED', 'Registered'),
        ('ATTENDED', 'Attended'),
        ('CANCELLED', 'Cancelled'),
        ('NO_SHOW', 'No Show'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='event_registrations')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='REGISTERED')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    rating = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'event_registrations'
        unique_together = [['event', 'user']]
        ordering = ['-registered_at']

    def __str__(self):
        return f'{self.user.email} - {self.event.title}'
