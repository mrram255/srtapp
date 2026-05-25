from django.db import models

from apps.core.models import CollegeScopedModel


class Attendance(CollegeScopedModel):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
        ('HALF_DAY', 'Half Day'),
    ]

    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendances',
    )
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.CASCADE,
        related_name='marked_attendances',
    )
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PRESENT')
    period = models.PositiveIntegerField(default=1)
    remarks = models.TextField(blank=True)
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendances'
        unique_together = [['student', 'subject', 'date', 'period']]
        ordering = ['-date', '-marked_at']

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.date} — {self.status}'


class AttendanceSummary(CollegeScopedModel):
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
    )
    subject = models.ForeignKey(
        'academics.Subject',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
    )
    academic_year = models.ForeignKey(
        'colleges.AcademicYear',
        on_delete=models.CASCADE,
        related_name='attendance_summaries',
    )
    total_classes = models.PositiveIntegerField(default=0)
    present_count = models.PositiveIntegerField(default=0)
    absent_count = models.PositiveIntegerField(default=0)
    late_count = models.PositiveIntegerField(default=0)
    excused_count = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'attendance_summaries'
        unique_together = [['student', 'subject', 'academic_year']]

    def __str__(self):
        return f'{self.student.enrollment_number} — {self.subject.name} — {self.percentage}%'
