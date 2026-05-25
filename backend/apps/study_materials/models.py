from django.db import models
from apps.core.models import CollegeScopedModel


class StudyMaterial(CollegeScopedModel):
    TYPE_CHOICES = [
        ('PDF', 'PDF Document'),
        ('VIDEO', 'Video'),
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Word/PPT Document'),
        ('LINK', 'External Link'),
        ('OTHER', 'Other'),
    ]
    ACCESS_CHOICES = [
        ('ALL', 'All Students'),
        ('DEPARTMENT', 'Department Only'),
        ('BATCH', 'Specific Batch/Section'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(
        'academics.Subject', on_delete=models.CASCADE, related_name='study_materials'
    )
    teacher = models.ForeignKey(
        'teachers.Teacher', on_delete=models.CASCADE, related_name='study_materials'
    )
    department = models.ForeignKey(
        'colleges.Department', on_delete=models.CASCADE, related_name='study_materials'
    )
    material_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='PDF')
    file_url = models.CharField(max_length=500, blank=True)
    external_link = models.URLField(blank=True)
    file_size = models.PositiveBigIntegerField(default=0, help_text='Size in bytes')
    version = models.PositiveIntegerField(default=1)
    semester = models.PositiveIntegerField()
    section = models.CharField(max_length=10, blank=True)
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='ALL')
    is_published = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    tags = models.CharField(max_length=500, blank=True, help_text='Comma-separated tags')

    class Meta:
        db_table = 'study_materials'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} v{self.version} — {self.subject.name}'
