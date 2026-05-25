from django.db import models

from apps.core.models import CollegeScopedModel


class Assignment(CollegeScopedModel):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('CLOSED', 'Closed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    department = models.ForeignKey(
        'colleges.Department',
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10)
    max_marks = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    attachment = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'assignments'
        ordering = ['-due_date']

    def __str__(self):
        return f'{self.title} ({self.subject.name})'


class AssignmentSubmission(CollegeScopedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SUBMITTED', 'Submitted'),
        ('LATE', 'Late Submission'),
        ('GRADED', 'Graded'),
        ('RESUBMIT', 'Resubmit Required'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    submission_text = models.TextField(blank=True)
    attachment = models.CharField(max_length=500, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    graded_by = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions',
    )
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'assignment_submissions'
        unique_together = [['assignment', 'student']]
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.assignment.title}'
