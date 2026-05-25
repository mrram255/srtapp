from django.db import models

from apps.core.models import CollegeScopedModel


class GateLog(CollegeScopedModel):
    ENTRY_TYPES = [
        ('ENTRY', 'Entry'),
        ('EXIT', 'Exit'),
    ]

    PERSON_TYPES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher'),
        ('STAFF', 'Staff'),
        ('VISITOR', 'Visitor'),
        ('VENDOR', 'Vendor'),
        ('OTHER', 'Other'),
    ]

    entry_type = models.CharField(max_length=10, choices=ENTRY_TYPES)
    person_type = models.CharField(max_length=10, choices=PERSON_TYPES)
    person = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gate_logs',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gate_logs',
    )

    visitor_name = models.CharField(max_length=200, blank=True)
    visitor_phone = models.CharField(max_length=15, blank=True)
    visitor_id_type = models.CharField(max_length=50, blank=True)
    visitor_id_number = models.CharField(max_length=100, blank=True)
    purpose = models.TextField(blank=True)
    meeting_with = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='visitor_meetings',
    )

    vehicle_number = models.CharField(max_length=20, blank=True)
    vehicle_type = models.CharField(max_length=20, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    expected_return = models.DateTimeField(null=True, blank=True)
    actual_return = models.DateTimeField(null=True, blank=True)

    security_guard = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gate_duty_logs',
        limit_choices_to={'role': 'SECURITY'},
    )
    gate_number = models.CharField(max_length=20, blank=True)
    verified_by = models.CharField(max_length=200, blank=True)
    remarks = models.TextField(blank=True)

    class Meta:
        db_table = 'gate_logs'
        ordering = ['-timestamp']

    def __str__(self):
        if self.person_id:
            return f'{self.entry_type} - {self.person.email} at {self.timestamp}'
        return f'{self.entry_type} - Visitor: {self.visitor_name} at {self.timestamp}'
