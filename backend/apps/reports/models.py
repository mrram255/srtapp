from django.db import models

from apps.core.models import CollegeScopedModel


def default_empty_dict():
    return {}


class ReportTemplate(CollegeScopedModel):
    REPORT_TYPES = [
        ('NAAC', 'NAAC Report'),
        ('NIRF', 'NIRF Report'),
        ('ATTENDANCE', 'Attendance Report'),
        ('FEE', 'Fee Collection Report'),
        ('RESULT', 'Result Analysis'),
        ('PLACEMENT', 'Placement Report'),
        ('ADMISSION', 'Admission Report'),
        ('CUSTOM', 'Custom Report'),
    ]

    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=15, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    parameters = models.JSONField(default=default_empty_dict, blank=True)
    template_file = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'report_templates'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.report_type})'


class GeneratedReport(CollegeScopedModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('GENERATING', 'Generating'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='generated_reports')
    name = models.CharField(max_length=255)
    parameters = models.JSONField(default=default_empty_dict)
    file_url = models.CharField(max_length=500, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    generated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='generated_reports',
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'generated_reports'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.status}'
